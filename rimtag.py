import asyncio
import logging, os

logging.basicConfig(
    level=logging.DEBUG, format='%(levelname)s: %(message)s'
    )

logging.getLogger('asyncio').setLevel(logging.WARNING) # Suppress epoll

from colorama import init
init()

import asyncclick as click

from cli import modlist, tags, mods

os.chdir(os.path.dirname(os.path.realpath(__file__)))

@click.group()
async def cli():
    pass

cli.add_command(modlist.modlist)
cli.add_command(tags.tags)
cli.add_command(mods.cli_mods)

if __name__ == '__main__':
    asyncio.run(cli())