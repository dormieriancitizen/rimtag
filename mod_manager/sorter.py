from pathlib import Path
import logging
from mod_manager.mod_handler import Mod

tier_3_mods = ["krkr.rocketman", "taranchuk.performanceoptimizer"]
dlcs=["ludeon.ideology","ludeon.anomaly","ludeon.biotech","ludeon.royalty"]

def sorter(mods: dict[Path,Mod]):
    # Convert all loadAfter into loadBefore

    deps: dict[str,list[str]] = {
        mod.pid: [] for _, mod in mods.items() if mod
    }

    for _, mod in mods.items():
        # Invert the load_befores
        for pid in mod.load_after:
            if pid in deps:
                deps[mod.pid].append(pid)
        
        for pid in mod.load_before:
            if pid in deps:
                deps[pid].append(mod.pid)

    # for d in modd:
    #     # If not otherwise specified, give every mod an orderAfter Core.
    #     if d not in modd["ludeon.rimworld"]["orderAfter"]:
    #         if "ludeon.rimworld" not in modd[d]["orderAfter"]:
    #             if d != "ludeon.rimworld":
    #                 modd[d]["orderAfter"].append("ludeon.rimworld")
        
    #                 # If not otherwise specified, also give every mod an orderAfter all DLCs.
    #                 dlc_names = ("biotech", "ideology", "royalty", "anomaly")
    #                 dlc_names = [f"ludeon.rimworld.{dlc_name}" for dlc_name in dlc_names]
                    
    #                 if d not in [item for sublist in [modd[dlc_name]["orderAfter"] for dlc_name in dlc_names] for item in sublist]:
    #                     if not Counter(dlc_names) & Counter(modd[d]["orderAfter"]):
    #                         if not d.startswith("ludeon.rimworld"):
    #                             modd[d]["orderAfter"].extend(dlc_names)

    for pid in deps:
        if pid in deps["ludeon.rimworld"] or pid.startswith("ludeon."):
            continue

        if "ludeon.rimworld" not in deps[pid]:
            deps[pid].append("ludeon.rimworld")

        for dlc in dlcs:
            if dlc in deps:
                if pid in deps[dlc]:
                    continue
                if dlc in deps[pid]:
                    continue

                deps[pid].append(dlc)

        

    load_normal_mods = [pid for pid in deps if pid not in tier_3_mods]
    for pid in tier_3_mods:
        if pid in deps:
            deps[pid].extend(load_normal_mods)

    order = sort_mod_list(deps)

    pids_by_path = {mods[path].pid: path for path in mods}

    final_order = {
        pids_by_path[pid]: mods[pids_by_path[pid]]
        for pid in order
    }

    return final_order

def find_circular_dependencies(nodes):
    def dfs(node, visited, rec_stack, path, cycles):
        visited.add(node)
        rec_stack.add(node)
        path.append(node)
        
        # Explore all the neighbors of the current node
        for neighbor in nodes.get(node, []):
            if neighbor not in visited:
                # If not visited, do DFS on this neighbor
                dfs(neighbor, visited, rec_stack, path, cycles)
            elif neighbor in rec_stack:
                # If the neighbor is in the current recursion stack, a cycle is found
                cycle_start_idx = path.index(neighbor)
                cycle = path[cycle_start_idx:] + [neighbor]
                cycles.append(cycle)
        
        # Remove the node from the recursion stack before backtracking
        rec_stack.remove(node)
        path.pop()

    logger = logging.getLogger()

    visited = set()
    rec_stack = set()
    cycles = []
    
    # Check each node to ensure we don't miss any disconnected parts of the graph
    for node in nodes:
        if node not in visited:
            dfs(node, visited, rec_stack, [], cycles)

    if cycles:
        for cycle in cycles:
            logger.error(f"Circular dependency detected: {' -> '.join(cycle)}")

def sort_mod_list(nodes: dict[str, list[str]]) -> list[str]:
    """
    Topological sort for a network of nodes

        nodes = {"A": ["B", "C"], "B": [], "C": ["B"]}
        topological_sort(nodes)
        # ["A", "C", "B"]

    :param nodes: Nodes of the network
    :return: nodes in topological order
    """

    logger = logging.getLogger()

    # Calculate the indegree for each node
    indegrees = {k: 0 for k in nodes.keys()}
    for pid, dependencies in nodes.items():
        for dependency in dependencies:
            indegrees[dependency] += 1

    # Place all elements with indegree 0 in queue
    queue: list[str] = [k for k in nodes.keys() if indegrees[k] == 0]
    # Sort queue alphabetically

    final_order: list[str] = []

    # Continue until all nodes have been dealt with
    while len(queue) > 0:
        # Sort the queue alphabetically by real name
        queue = sorted(queue,key=lambda x: x,reverse=True)

        # node of current iteration is the first one from the queue
        curr: str = queue.pop(0)
        final_order.append(curr)

        # remove the current node from other dependencies
        for dependency in nodes[curr]:
            indegrees[dependency] -= 1

            if indegrees[dependency] == 0:
                queue.append(dependency)
        

    # check for circular dependencies
    if len(final_order) != len(nodes):
        logger.critical("Found circular dependencies.")
        find_circular_dependencies(nodes)
        raise Exception("Circular dependency found.")
    
    # Reverse the list since we have it in reverse order
    final_order.reverse()

    return final_order