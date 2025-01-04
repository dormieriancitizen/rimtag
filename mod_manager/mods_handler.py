import logging, dbm
import time
from typing import Any

import asyncio, os

import mod_manager.steam_handler as steam_handler
from mod_manager.cache import update_json_cache

# import mod_manager.mod_handler as mod_handler

from mod_manager.mod_handler import Mod, generate_mod_from_cache, generate_mod_from_scratch, is_steam_mod

from pathlib import Path
import json

def jsonable_mods_info(mods_info):
    jsonables = {}
    for mod in mods_info:
        jsonable = mods_info[mod].jsonable()
        jsonables[jsonable["path"]] = jsonable
    
    return jsonables

async def get_mods_info(scandirs: list[Path]) -> dict[Path, Mod]:
    mod_paths = []
    for dir in scandirs:
        for subdir in next(os.walk(dir))[1]:
            mod_paths.append(Path(dir) / subdir)
    
    return await get_mods_info_from_paths(mod_paths)

async def get_mods_info_from_paths(paths: list[Path]) -> dict[Path, Mod]:
    logger = logging.getLogger()
    start_time = time.time()

    cache_file = Path("cache/mods_info.json")

    if cache_file.exists():
        try:
            cache: dict[str, Any] = json.loads(cache_file.read_bytes())
        except json.JSONDecodeError:
            logger.warning("Failed to read mods_info cache")
            cache = {}
    else:
        cache = {}

    steam_mods: list[Path] = []

    to_update = []
    for path in paths:
        if str(path.absolute()) not in cache:
            to_update.append(path)
            continue
        if path.stat().st_mtime > cache[str(path.absolute())]["time_updated"]:
            to_update.append(path)
            continue

    # Todo: replace this with a flag
    if True:
        for path in to_update:
            if is_steam_mod(path):
                steam_mods.append(path)
        
        if steam_mods:
            steam_source = asyncio.create_task(steam_handler.fetch_from_steam([path.name for path in steam_mods]))
    else:
        # get steam from cache
        pass

    mods_info: dict[Path, Any] = {}
    mods_tasks = []

    # Not closing bc I'll bneed this later
    db =  dbm.open(Path("cache/persistent.dbm"),"c")

    for path in paths:
        abs_path = path.absolute().as_posix()
        if abs_path not in db:
            db[abs_path] = "{}"

        mod_persistent_info = db[abs_path]

        if path in to_update:
            if path in steam_mods:
                mod_maker = generate_mod_from_scratch(
                    path, 
                    mod_steam_info=asyncio.create_task(steam_handler.mod_steam_info(path, steam_source)),
                    dbm_db = db,
                    mod_persistent_info=mod_persistent_info
                )
            else:
                mod_maker = generate_mod_from_scratch(
                    path,
                    dbm_db=db,
                    mod_persistent_info=mod_persistent_info
                )
        else:
            mod_maker = generate_mod_from_cache(
                cache[str(path)],
                dbm_db = db,
                mod_persistent_info=mod_persistent_info
            )

        mods_tasks.append(asyncio.create_task(mod_maker))

    mods_info = {mod.path: mod for mod in (await asyncio.gather(*mods_tasks))}

    asyncio.create_task(update_json_cache(cache_file,jsonable_mods_info(mods_info)))

    logger.info(f"Finished processing mod metadata in {time.time()-start_time}. {len(to_update)}/{len(paths)} updated.")

    return mods_info
