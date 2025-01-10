import logging
import itertools

from pathlib import Path
from typing import Iterable
from xml.parsers.expat import ExpatError

from aiofile import async_open
from colorama import Fore, Back, Style

import xmltodict

from config import FRAMEWORK_MODS
from mod_manager.mod import Mod

async def validate_tags(mod_data: dict[Path,Mod]) -> None:
    def find_dupes(input: Iterable):
        unique = set()
        dupes = []

        for x in input:
            if x in unique:
                dupes.append(x)
            else:
                unique.add(x)

        return dupes, unique

    logger = logging.getLogger()

    replacements_folder = Path("cache/databases/UseThisInstead/Replacements/")

    for tag_file in [f for f in Path("cache/tags").iterdir() if f.is_file()]:
        logger.info(f"Validating tag {Fore.RED}{tag_file.name}{Style.RESET_ALL}")

        tag_paths = [Path(posix) for posix in tag_file.read_text().split("\n")]

        dupes, unique = find_dupes(tag_paths)

        if dupes:
            for dupe in dupes:
                logger.info(f"Found duplicate: {dupe}. Removing from tag")

            tag_file.write_text("\n".join([path.absolute().as_posix() for path in unique]))


        tag_mods: dict[Path,Mod] = {path: mod_data[path] for path in tag_paths}
        tag_pids = set(mod.pid for mod in tag_mods.values())

        for mod in tag_mods.values():
            if mod.source == "STEAM":
                 
                replacement_path = replacements_folder / (mod.steam_id+".xml")
                if replacement_path.is_file():
                    async with async_open(replacement_path,"rb") as replacement_file:
                        try:
                            replacement_xml = xmltodict.parse((await replacement_file.read()), dict_constructor=dict)
                            replacement_link = "https://steamcommunity.com/sharedfiles/filedetails/?id="+replacement_xml["ModReplacement"]["ReplacementSteamId"]

                            logger.info(f"Mod {mod.gname} has replacement available: {replacement_link}")
                        except ExpatError:
                            logger.error(f"Expat error in "+replacement_path.as_posix())

            for dependency in mod.deps:
                if dependency not in itertools.chain(FRAMEWORK_MODS):
                    if dependency not in tag_pids:
                        logger.info(f"Mod {mod.gname} missing dependency {Fore.GREEN}{dependency}{Style.RESET_ALL}")

def merge_tags(include: Iterable[list[Path]], exclude: Iterable[list[Path]]) -> list[Path]:
    modlist: set[Path] = set()

    for tag in include:
        modlist.update(tag)

    for tag in exclude:
        for path in tag:
            if path in modlist:
                modlist.discard(path)

    return list(modlist)

def get_tag_info(tag_name: str) -> list[Path]:
    tag_path = Path(f"cache/tags") / tag_name

    if tag_path.is_file():
        return [Path(posix) for posix in tag_path.read_text().splitlines()]
    else:
        return []