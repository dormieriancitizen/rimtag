import asyncio
import itertools
import os
from pathlib import Path
import time
from typing import Awaitable, Iterable
from urllib.parse import urlparse

import logging

from colorama import Fore, Back, Style

from mod_manager.mod import Mod
from mod_manager import steam_handler
from config import WORKSHOP_PATH, STEAMCMD_PATH, GITHUB_MODS_PATH

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

# async def command_run(cmd: list[str]) -> int | None:
#     logger = logging.getLogger()
#     proc = await asyncio.create_subprocess_exec(
#         *cmd,
#         stdout=asyncio.subprocess.PIPE,
#         stderr=asyncio.subprocess.PIPE)

#     stdout, stderr = await proc.communicate()

#     logger.debug(f'[{cmd!r} exited with {proc.returncode}]')
#     if stdout:
#         logger.debug(f'[stdout]\n{stdout.decode()}')
#     if stderr:
#         logger.debug(f'[stderr]\n{stderr.decode()}')

#     return proc.returncode

async def command_run(cmd: list[str]) -> int | None:
    # Magic chatgpt code
    logger = logging.getLogger()
    proc = await asyncio.create_subprocess_exec(
        *cmd,
        stdout=asyncio.subprocess.PIPE,
        stderr=asyncio.subprocess.PIPE)

    async def log_stream(stream, log_level):
        while True:
            line = await stream.readline()
            if not line:  # End of stream
                break
            logger.log(log_level, line.decode().strip())

    stdout_task = asyncio.create_task(log_stream(proc.stdout, logging.INFO))
    stderr_task = asyncio.create_task(log_stream(proc.stderr, logging.ERROR))

    await asyncio.gather(stdout_task, stderr_task)
    returncode = await proc.wait()

    # logger.debug(f'[{cmd!r} exited with {returncode}]')
    return returncode

async def steam_download_workshop_ids(workshop_ids: Iterable[str]) -> list[Path]:
    if not workshop_ids:
        return []

    command = [STEAMCMD_PATH,
            "+logon", "anonymous",
        ]

    for id in workshop_ids:
        command.extend(["+workshop_download_item", "294100", id])
    
    command.append("+exit")

    await command_run(command)

    downloaded_paths = [WORKSHOP_PATH / id for id in workshop_ids]

    return downloaded_paths

async def github_download_links(links: list[str]) -> list[Path]:
    def get_github_repo_name(url: str) -> str:
        # Parse the URL to get its components
        parsed_url = urlparse(url)
        
        # The path of the URL will contain '/username/repository'
        path_parts = parsed_url.path.strip('/').split('/')
        
        # The repository name is the second part of the path
        if len(path_parts) == 2:
            return path_parts[1]
        else:
            return ""  # Return None if the URL format is not correct
    
    logger = logging.getLogger()

    downloaded_paths = []
    dl_tasks = []

    for link in links:
        repo_name = get_github_repo_name(link)
        logger.info(f"Download {repo_name}")
        downloaded_path = GITHUB_MODS_PATH / repo_name

        command = ["git", "-C", GITHUB_MODS_PATH, "clone", link]

        dl_task = asyncio.create_task(command_run(command))

        dl_tasks.append(dl_task)
        downloaded_paths.append(downloaded_path)
    
    await asyncio.gather(*dl_tasks)

    return downloaded_paths

def unlink_folder(folder: Path) -> None:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to unlink %s. Reason: %s' % (file_path, e))

async def dds_encode(path):
    cmd = todds_command.copy()

    cmd.extend(["-p", path.absolute().as_posix()])

    # print(" ".join(cmd))

    await command_run(cmd)

async def process_downloads(*args: Awaitable[list[Path]]):
    paths_2d: list[list[Path]] = await asyncio.gather(*args)

    paths: list[Path] = list(itertools.chain(*paths_2d))

    unlink_folder(Path("active"))

    for path in paths:
        active_path = Path("active") / path.name

        os.symlink(path,active_path)
        await dds_encode(active_path)

async def update_mods(mods: list[Mod]):
    to_download_steam = []
    to_download_github = []
    
    for mod in mods:
        if mod.source == "STEAM":
            to_download_steam.append(mod.steam_id)
        elif mod.source == "GITHUB":
            to_download_github.append(mod.steam_id)

    await process_downloads(steam_download_workshop_ids(to_download_steam))

    for mod in itertools.chain(mods):
        mod.download_time = time.time()

async def update(mods):
    logger = logging.getLogger()
    
    steam_mods: dict[str,Mod] = {}

    for path, mod in mods.items():
        if mod.source == "STEAM":
            steam_mods[mod.steam_id] = mod

    steam_info = await steam_handler.fetch_from_steam(
        list(steam_mods.keys())
    )

    to_download = []

    for steam_id, mod in steam_mods.items():
        if mod.download_time:
            if str(steam_id) not in steam_info:
                continue
            else:
                mod_steam_info = steam_info[str(steam_id)]
        
            if "time_updated" not in mod_steam_info:
                logger.warning(f"Mod {mod.gname} ({steam_id}) does not have update time")
                continue
        
            if float(mod_steam_info["time_updated"]) > mod.download_time:
                to_download.append(mod)
        else:
            to_download.append(mod)
    
    logger.info("\n".join(f"{Fore.BLUE}{mod.gname}{Style.RESET_ALL}" for mod in to_download))
    await update_mods(to_download)
    