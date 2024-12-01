import logging, asyncio, os

logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s: %(message)s'
    )

logging.getLogger('asyncio').setLevel(logging.WARNING) # Suppress epoll

import mod_manager.rentry, mod_manager.sorter, mod_manager.mods_handler, mod_manager.modlist_handler

from config import MOD_SCAN_DIRS

def main():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))

    mods = asyncio.run(mod_manager.mods_handler.get_mods_info(MOD_SCAN_DIRS))

    # modlist = {path: mod for path, mod in mods.items() if mod.name.startswith("ludeon")}

    # mod_manager.rentry.upload(mod_manager.rentry.compile_rentry(mod_manager.sorter.sorter(mods)))
    mod_manager.modlist_handler.link_mods(list(mods.values()))

if __name__ == "__main__":
    main()