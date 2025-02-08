import logging
import time
from xxlimited import new
import asyncclick as click
import asyncio
from pathlib import Path

from cli import interface
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
        mod.download_time = target_time

@cli_mods.command("add")
@click.argument("steam_ids",nargs=-1)
async def add_mod(steam_ids: list[str]):
    await download.process_downloads(
        download.steam_download_workshop_ids(steam_ids)
    )

    mod_data: dict[Path, Mod] = await metadata.get_mods_info_from_paths([WORKSHOP_PATH / steam_id for steam_id in steam_ids])

    for mod in mod_data.values():
        mod.download_time = time.time()

    if click.confirm("Choose tags to add mods to?"):
        for mod in mod_data.values():
            await interface.select_and_add_mod_to_tag(mod)

@cli_mods.command("by_dep")
async def cli_get_mods_by_dep():
    mod_data = await metadata.get_mods_info(MOD_SCAN_DIRS)

    target_pid: str = (await inquirer.fuzzy( # type: ignore
                message=f"Choose parent mod",
                choices=[Choice(mod.pid,mod.ident) for mod in mod_data.values()],
                pointer=">",
            ).execute_async())
    
    for path, mod in mod_data.items():
        if target_pid in mod.deps:
            print(f"{mod.gname}")

@cli_mods.command("prio")
async def cli_set_mod_prio():
    logger = logging.getLogger()
    mod_data = await metadata.get_mods_info(MOD_SCAN_DIRS)

    mod_path: Path = (await inquirer.fuzzy( # type: ignore
                message=f"Choose parent mod",
                choices=[Choice(path,m.ident) for path, m in mod_data.items()],
                pointer=">",
            ).execute_async())

    mod = mod_data[mod_path]

    logger.info(f"Current prio: {mod.sort_priority}")
    new_prio = int(click.prompt("Enter new priority"))

    mod.sort_priority = new_prio

    logger.info(f"Updated priority of {mod.gname} to {Style.BRIGHT}{new_prio}{Style.RESET_ALL}")
