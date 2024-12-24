from ast import Mod
import logging, os

from pathlib import Path
from typing import Iterable
from mod_manager.mod_handler import Mod

from config import RIMWORLD_GAME_PATH
from mod_manager.sorter import modsort

logger: logging.Logger = logging.getLogger()

def make_modconfig_file(order: list[str]) -> str:
    c = f"""<?xml version="1.0" encoding="utf-8"?>
<ModsConfigData>
    <version>{(RIMWORLD_GAME_PATH / "Version.txt").read_text().rstrip()}</version>
    <activeMods>"""
    c += "\n"+"\n".join([f"        <li>{pid}</li>" for pid in order])+"\n"
    c += """    </activeMods>
    <knownExpansions>
        <li>ludeon.rimworld</li>
        <li>ludeon.rimworld.royalty</li>
        <li>ludeon.rimworld.ideology</li>
        <li>ludeon.rimworld.biotech</li>
        <li>ludeon.rimworld.anomaly</li>
    </knownExpansions>
</ModsConfigData>"""
    return c

mods_folder = Path("/home/dormierian/Games/rimworld/Mods")

def unlink_folder(folder: Path) -> None:
    for filename in os.listdir(folder):
        file_path = os.path.join(folder, filename)
        try:
            if os.path.islink(file_path):
                os.unlink(file_path)
        except Exception as e:
            print('Failed to unlink %s. Reason: %s' % (file_path, e))

def link_mods(mods: list[Mod]) -> None:
    unlink_folder(mods_folder)
    for mod in mods:
        if mod.source != "LUDEON":
            os.symlink(src=mod.path,dst=mods_folder / mod.path.name)

def merge_tags(include: Iterable[list[Path]], exclude: Iterable[list[Path]]) -> list[Path]:
    modlist: set[Path] = set()

    for tag in include:
        modlist.update(tag)

    for tag in exclude:
        for path in tag:
            if path in modlist:
                modlist.discard(path)

    return list(modlist)

async def get_instance_mods(mod_data: dict[Path,Mod],instance_name: str) -> dict[Path,Mod]:
    instance_tags = Path(f"cache/instances/{instance_name}").read_text().splitlines()

    include = instance_tags[0].split(",")

    if len(instance_tags) > 1:
        exclude = instance_tags[1].split(",")
    else:
        exclude = []

    modlist = merge_tags(
        include=(get_tag_info(tag) for tag in include),
        exclude=(get_tag_info(tag) for tag in exclude)
    )

    mod_data = {path: mod for path, mod in mod_data.items() if path in modlist}

    return mod_data

def get_tag_info(tag_name: str) -> list[Path]:
    tag_path = Path(f"cache/tags") / tag_name

    if tag_path.is_file():
        return [Path(posix) for posix in tag_path.read_text().splitlines()]
    else:
        return []
