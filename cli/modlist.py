from pathlib import Path
import asyncclick as click

from config import MOD_SCAN_DIRS, RIMWORLD_CONFIG_PATH

from mod_manager import download_handler, mods_handler
from mod_manager.modlist_handler import merge_tags, get_tag_info, make_modconfig_file, get_instance_mods
from mod_manager.sorter import modsort
from mod_manager import rentry

import cli.interface as interface

@click.command("update")
async def update():
    mods = mods_handler.get_mods_info(MOD_SCAN_DIRS)
    await download_handler.update(mods)

@click.group("instance")
async def modlist():
    pass

@modlist.command("list")
async def make_modlist():
    modlist_name = await interface.prompt_instance_name()

    mod_data = await get_instance_mods(
        (await mods_handler.get_mods_info(MOD_SCAN_DIRS)),
        modlist_name
    )
    
    sort_order = modsort(mod_data)

    with open(RIMWORLD_CONFIG_PATH / "Config/ModsConfig.xml","w") as modsconfig_file:
        modsconfig_file.write(make_modconfig_file(sort_order))

@modlist.command("rentry")
async def upload_rentry():
    modlist_name = await interface.prompt_instance_name()

    mod_data = await get_instance_mods(
        (await mods_handler.get_mods_info(MOD_SCAN_DIRS)),
        modlist_name
    )

    mod_data_by_pid = {mod.pid: mod for mod in mod_data.values()}

    sort_order = modsort(mod_data)

    sorted_mod_data = {mod_data_by_pid[pid].path: mod_data_by_pid[pid] for pid in sort_order}

    rentry.upload(rentry.compile_rentry(sorted_mod_data))

@modlist.command("set_tags")
async def _set_tags():
    await click.prompt(" ")