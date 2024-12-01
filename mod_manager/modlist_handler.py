from ast import Mod
import logging, os

from pathlib import Path
from mod_manager.mod_handler import Mod

logger: logging.Logger = logging.getLogger()


def modconfig_file(order: list[str]) -> str:
    c = """<?xml version="1.0" encoding="utf-8"?>
<ModsConfigData>
    <version>1.5.4104 rev435</version>
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