import logging
import os
from pathlib import Path

from InquirerPy import inquirer
import asyncclick as click

from config import CONFIG_PATH
from mod_manager.mod import Mod

async def select_or_create(scan_path: Path,query: str) -> str | None:
    paths = [f.name for f in scan_path.iterdir() if f.is_file()]

    paths.append("Create New")
    paths.append("None")

    result: str = (await inquirer.fuzzy( # type: ignore
                message=f"Choose {query}",
                choices=paths,
                pointer=">",
            ).execute_async())

    if result == "None":
        return None

    if result == "Create New":
        result = click.prompt(f"Enter name for new {query}")

        with open(scan_path / result, "w") as f:
            f.write("")

    return result

async def prompt_instance_name() -> str | None:
    logger = logging.getLogger()
    instance_name = ""

    cache_path = (CONFIG_PATH / "instance_name")
    
    instance_paths = [f for f in os.listdir("cache/instances") if os.path.isfile(os.path.join("cache/instances", f))]

    instance_paths.append("Create New")

    if cache_path.exists():
        cached_instance_name = cache_path.read_text()

        if click.confirm(f"Use cached instance {cached_instance_name}?"):
            instance_name = cached_instance_name
            logger.info(f"Using cached instance {instance_name}")
    
    if not instance_name:
        with open(f"cached_instance_name","w") as instance_cache:
            instance_name = await select_or_create((CONFIG_PATH / "instances"),"instance")

            if instance_name:
                instance_cache.write(instance_name)
            else:
                return None
    return instance_name

async def select_and_add_mod_to_tag(mod: Mod):
    print(f"Select tag for {mod.gname}")
    tag_name = await select_or_create(
        (CONFIG_PATH / "tags/"),"tag"
    )

    if tag_name:
        with open((CONFIG_PATH / "tags") / tag_name, "a") as tag_file:
            tag_file.write("\n"+mod.path.absolute().as_posix())
