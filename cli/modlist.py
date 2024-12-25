from pathlib import Path
import asyncclick as click

from colorama import Fore, Style, Back

from config import MOD_SCAN_DIRS, RIMWORLD_CONFIG_PATH

from mod_manager import download_handler, mods_handler
from mod_manager import modlist_handler
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

    if not modlist_name:
        return

    mod_data = await get_instance_mods(
        (await mods_handler.get_mods_info(MOD_SCAN_DIRS)),
        modlist_name
    )
    
    sort_order = modsort(mod_data)

    with open(RIMWORLD_CONFIG_PATH / "Config/ModsConfig.xml","w") as modsconfig_file:
        modsconfig_file.write(make_modconfig_file(sort_order))

    modlist_handler.link_mods(list(mod_data.values())) # t

@modlist.command("rentry")
async def upload_rentry():
    modlist_name = await interface.prompt_instance_name()


    if not modlist_name:
        return

    mod_data = await get_instance_mods(
        (await mods_handler.get_mods_info(MOD_SCAN_DIRS)),
        modlist_name
    )

    mod_data_by_pid = {mod.pid: mod for mod in mod_data.values()}

    sort_order = modsort(mod_data)

    sorted_mod_data = {mod_data_by_pid[pid].path: mod_data_by_pid[pid] for pid in sort_order}

    rentry.upload(rentry.compile_rentry(sorted_mod_data))

@modlist.command("compare")
async def compare_modlists():
    target_modlist = click.prompt("Enter modlist").split(",")

    modlist_name = await interface.prompt_instance_name()

    if not modlist_name:
        return

    mod_data = await mods_handler.get_mods_info(MOD_SCAN_DIRS)

    instance_mod_data = await get_instance_mods(
        mod_data,
        modlist_name
    )

    old_modlist_version = {mod.path.name: mod for mod in instance_mod_data.values()}

    missing_mods: list[str] = [mod_id for mod_id in target_modlist if mod_id not in old_modlist_version]
    old_mod_data_version = {mod.path.name: mod for mod in mod_data.values()}

    print("\n".join((old_mod_data_version[mod_id].name if mod_id in old_mod_data_version else mod_id) for mod_id in missing_mods))

    for mod in [old_mod_data_version[mod_id] for mod_id in missing_mods if mod_id in old_mod_data_version]:
        print(f"Select tag for {Fore.BLUE}{mod.name}{Style.RESET_ALL}")

        tag_name = await interface.select_or_create(
            Path("cache/tags/"),"tag"
        )

        if tag_name:
            with open(Path("cache/tags") / tag_name, "a") as tag_file:
                tag_file.write("\n"+mod.path.absolute().as_posix())



@modlist.command("set_tags")
async def _set_tags():
    await click.prompt(" ")