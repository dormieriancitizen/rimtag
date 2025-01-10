from pathlib import Path

from InquirerPy import inquirer
from InquirerPy.base.control import Choice
import asyncclick as click

from config import MOD_SCAN_DIRS
from mod_manager import metadata, tag

from mod_manager.tag import get_tag_info
from cli.interface import select_or_create

@click.group("tags")
def tags():
    pass

@tags.command("info")
@click.argument("tag_name",nargs = -1)
async def show_tag_info(tag_name):
    mods_info = await metadata.get_mods_info(MOD_SCAN_DIRS)
    
    if tag_name:
        tag_name = tag_name[0]
    else:
        tag_name = (await select_or_create(Path("cache/tags/"),"tag"))

    if not tag_name:
        return

    tag_info = get_tag_info(tag_name)

    print("\n".join((
        mods_info[mod_path].name for mod_path in tag_info
    )))

@tags.command("validate")
async def validate_tags():
    mods_data = await metadata.get_mods_info(MOD_SCAN_DIRS)
    await tag.validate_tags(mods_data)

@tags.command("edit")
@click.argument("tag_name",nargs = -1)
async def edit_tag(tag_name):
    mods_info = await metadata.get_mods_info(MOD_SCAN_DIRS)
    
    if tag_name:
        tag_name = tag_name[0]
    else:
        tag_name = (await select_or_create(Path("cache/tags/"),"tag"))

    if not tag_name:
        return

    tag_info = get_tag_info(tag_name)

    choices = [
        Choice(
            mod.path.absolute().as_posix(),
            name=mod.ident,
            enabled=(path in tag_info),
        ) for path, mod in mods_info.items()
    ]

    keybindings = {
        "toggle": [
            {"key": "c-space"}
        ],
        "answer": [
            {"key": "enter"}
        ]
    }

    mods: list[Path] = await inquirer.fuzzy( # type: ignore
                message="Choose mods",
                choices=choices,
                pointer=">",
                multiselect=True,
                keybindings=keybindings # type: ignore
            ).execute_async()

    print(f"Tag {tag_name} is {len(mods)} mods long")

    with open(Path("cache/tags/") / tag_name, "w") as tag_file:
        tag_file.write("\n".join(mods)) # type: ignore