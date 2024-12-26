import asyncclick as click
import asyncio

from config import MOD_SCAN_DIRS
from mod_manager import mods_handler, download_handler
from mod_manager.mod_handler import Mod

@click.group("mods")
def cli_mods():
    pass

@cli_mods.command("update")
async def update():
    mods = await mods_handler.get_mods_info(MOD_SCAN_DIRS)
    await download_handler.update(mods)

@cli_mods.command("encode")
async def encode():
    for path in MOD_SCAN_DIRS:
        await download_handler.dds_encode(path)

@cli_mods.command("set_time")
async def set_time():
    mod_data_task: dict[Path,Mod] = asyncio.create_task(mods_handler.get_mods_info(MOD_SCAN_DIRS))

    target_time = float(click.prompt("Enter time to set in unix seconds"))
    mod_data = await mod_data_task

    for mod in mod_data.values():
        mod.update_persistence("download_time",target_time)
