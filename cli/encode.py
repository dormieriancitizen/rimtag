import asyncclick as click

from config import MOD_SCAN_DIRS

from mod_manager.download_handler import dds_encode

@click.command("encode")
async def encode():
    for path in MOD_SCAN_DIRS:
        await dds_encode(path)