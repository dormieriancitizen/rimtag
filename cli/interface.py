import logging
import os
from pathlib import Path

from InquirerPy import inquirer
import asyncclick as click

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

    cache_path = Path("cache/instance_name")
    
    instance_paths = [f for f in os.listdir("cache/instances") if os.path.isfile(os.path.join("cache/instances", f))]

    instance_paths.append("Create New")

    if cache_path.exists():
        cached_instance_name = cache_path.read_text()

        if click.confirm(f"Use cached instance {cached_instance_name}?"):
            instance_name = cached_instance_name
            logger.info(f"Using cached instance {instance_name}")
    
    if not instance_name:
        with open(f"cached_instance_name","w") as instance_cache:
            instance_name = await select_or_create(Path("cache/instances"),"instance")

            if instance_name:
                instance_cache.write(instance_name)
            else:
                return None
    return instance_name