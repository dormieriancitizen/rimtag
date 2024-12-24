import logging
import os
from pathlib import Path

from InquirerPy import inquirer
import asyncclick as click

async def select_or_create(scan_path: Path) -> str:
    paths = [f.name for f in scan_path.iterdir() if f.is_file()]

    paths.append("Create New")

    result: str = (await inquirer.select( # type: ignore
                message="Choose instance",
                choices=paths,
                pointer=">",
            ).execute_async())

    if result == "Create New":
        result = click.prompt("Enter name for new instance")

        with open(scan_path / result, "w") as f:
            f.write("")

    return result

async def prompt_instance_name():
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
            
            instance_name = await select_or_create(Path("cache/instances"))

            instance_cache.write(instance_name)
    return instance_name