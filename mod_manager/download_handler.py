import asyncio
import itertools
import os
from pathlib import Path
import subprocess
from typing import Awaitable

from config import WORKSHOP_PATH, STEAMCMD_PATH

todds_command = [
    "todds", 
    "-f", "BC1", 
    "-af", "BC7",
    "-on",
    "-vf",
    "-fs",
    "-r", "Textures",
    "-t"
]

async def steam_download_workshop_ids(workshop_ids: list[str]) -> list[Path]:
    command = [STEAMCMD_PATH,
            "+logon", "anonymous",
        ]

    for id in workshop_ids:
        command.extend(["workhop_download_item", "294100", id])
    
    command.append("+exit")

    dl_task = await asyncio.create_subprocess_exec(
        *command,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    return_code = await dl_task.communicate()

    downloaded_paths = [WORKSHOP_PATH / id for id in workshop_ids]

    return downloaded_paths

def unlink_folder(folder: Path) -> None:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to unlink %s. Reason: %s' % (file_path, e))

def dds_encode(path):
    cmd = todds_command.copy()

    cmd.extend(["-p", path.absolute.as_posix])

    return subprocess.Popen(todds_command,)

async def process_downloads(*args: Awaitable[list[Path]]):
    paths_2d = await asyncio.gather(*args)

    paths: list[Path] = list(itertools.chain(*paths_2d))

    unlink_folder(Path("active"))

    for path in paths:
        os.symlink(path,Path("active"))

    encode_task = dds_encode(Path("active"))


        
    