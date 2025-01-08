import time
import asyncclick as click
import asyncio
from pathlib import Path

from config import MOD_SCAN_DIRS, WORKSHOP_PATH
from mod_manager import metadata, download, mod
from mod_manager.mod import Mod

from InquirerPy import inquirer
from InquirerPy.base.control import Choice

from colorama import Back, Fore, Style

@click.group("mods")
def cli_mods():
    pass

@cli_mods.command("update")
async def update():
    mods = await metadata.get_mods_info(MOD_SCAN_DIRS)
    await download.update(mods)

@cli_mods.command("encode")
async def encode():
    for path in MOD_SCAN_DIRS:
        await download.dds_encode(path)

@cli_mods.command("set_time")
async def set_time():
    mod_data_task = asyncio.create_task(metadata.get_mods_info(MOD_SCAN_DIRS))

    target_time = float(click.prompt("Enter time to set in unix seconds"))
    mod_data: dict[Path,Mod]  = await mod_data_task

    for mod in mod_data.values():
        mod.update_persistence("download_time",target_time)

@cli_mods.command("add")
@click.argument("steam_ids",nargs=-1)
async def add_mod(steam_ids: list[str]):
    await download.process_downloads(
        download.steam_download_workshop_ids(steam_ids)
    )

    mod_info: dict[Path, Mod] = await metadata.get_mods_info_from_paths([WORKSHOP_PATH / steam_id for steam_id in steam_ids])

    for mod in mod_info.values():
        mod.update_persistence("download_time",time.time())

@cli_mods.command("by_dep")
async def cli_get_mods_by_deb():
    mod_data = await metadata.get_mods_info(MOD_SCAN_DIRS)

    target_pid: str = (await inquirer.fuzzy( # type: ignore
                message=f"Choose parent mod",
                choices=[Choice(mod.pid,mod.name) for mod in mod_data.values()],
                pointer=">",
            ).execute_async())
    
    for path, mod in mod_data.items():
        if target_pid in mod.deps:
            print(f"{Fore.BLUE}{mod.name}{Style.RESET_ALL}")