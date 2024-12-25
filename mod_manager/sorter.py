from pathlib import Path
import logging
from itertools import chain

from mod_manager.mod_handler import Mod

from config import TIER_THREE_MODS, DLC_NAMES

def modsort(mods: dict[Path,Mod]) -> list[str]:
    # Convert all loadAfter into loadBefore
    logger = logging.getLogger()


    deps: dict[str,list[str]] = {
        mod.pid: [] for _, mod in mods.items() if mod
    }

    for path, mod in mods.copy().items():
        for dependency in mod.deps:
            if dependency not in deps:
                logger.warning(f"Mod {mod.name} missing dependency {dependency}, removing from list")
                del deps[mod.pid]
                del mods[path]

    for _, mod in mods.items():
        # Invert the load_befores
        for pid in mod.load_after:
            if pid in deps:
                deps[mod.pid].append(pid)
        
        for pid in mod.load_before:
            if pid in deps:
                deps[pid].append(mod.pid)
    
    for pid in deps:
        # Make sure all mods load before rimworld, that don't specify otherwise
        if pid in deps["ludeon.rimworld"] or pid.startswith("ludeon."):
            continue

        if "ludeon.rimworld" not in deps[pid]:
            deps[pid].append("ludeon.rimworld")

        for dlc in DLC_NAMES:
            if dlc in deps:
                if pid in deps[dlc]:
                    continue
                if dlc in deps[pid]:
                    continue

                deps[pid].append(dlc)

        

    load_normal_mods = [pid for pid in deps if pid not in TIER_THREE_MODS]
    for pid in TIER_THREE_MODS:
        if pid in deps:
            deps[pid].extend(load_normal_mods)

    order = sort_mod_list(deps)

    # pids_by_path = {mods[path].pid: path for path in mods}

    # final_order = {
    #     pids_by_path[pid]: mods[pids_by_path[pid]]
    #     for pid in order
    # }

    return order

def find_circular_dependencies(nodes):
    # Magic chatgpt code (it works idk)
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