import asyncclick as click

from config import MOD_SCAN_DIRS

from mod_manager import download_handler, mods_handler

@click.group()
def cli():
    pass

@cli.command("update")
async def update():
    mods = mods_handler.get_mods_info(MOD_SCAN_DIRS)
    await download_handler.update(mods)

@cli.group("list")
async def modlist():
    pass

@modlist.command("")
async def make_modlist(*args):
    mods = mods_handler.get_mods_info(MOD_SCAN_DIRS)
    