from pathlib import Path
import subprocess
from typing import Any, Union

from aiofile import async_open

import time, xmltodict, logging
from xml.parsers.expat import ExpatError

class Mod:
    def __init__(self,
                 path: Path,
                 source: str,
                 pid: str,
                 name: str,
                 deps: list[str],
                 load_before: list[str],
                 load_after: list[str],
                 supported_versions: list[str],
                 time_first_downloaded: float,
                 time_updated: float,
                 download_link: str,
                 pfid: str,
                 filesize: float) -> None:
        
        self.path: Path = path
        self.source: str = source

        self.pid: str = pid
        self.name: str = name

        self.deps: list[str] = deps
        self.load_before: list[str] = load_before
        self.load_after: list[str] = load_after

        self.supported_versions: list[str] = supported_versions

        self.time_first_downloaded: float = time_first_downloaded
        self.time_updated: float = time_updated

        self.download_link: str = download_link

        self.pfid: str = pfid
        self.filesize: float = filesize

    def jsonable(self) -> dict[str,Any]:
        cached = {}

        cached["path"] = str(self.path.absolute())
        cached["source"] = self.source

        cached["pid"] = self.pid
        cached["name"] = self.name

        cached["deps"] = self.deps
        cached["load_before"] = self.load_before
        cached["load_after"] = self.load_after

        cached["supported_versions"] = self.supported_versions

        cached["time_first_downloaded"] = self.time_first_downloaded
        cached["time_updated"] = self.time_updated

        cached["download_link"] = self.download_link

        cached["pfid"] = self.pfid
        cached["filesize"] = self.filesize

        return cached

    def best_supported_version(self) -> str:
        return str(max([float(ver) for ver in self.supported_versions], default="1.5"))
            

    def __repr__(self):
        return str(self.jsonable())

async def mod_about(path: Path) -> dict[Any,Any]:
    logger = logging.getLogger()

    about_file = path / "About" / "About.xml"

    if not about_file.exists():
        about_file = path / "About" / "about.xml"

    if not about_file.exists():
        logger.critical(f"Could not find about.xml for {str(path)}")
        raise OSError("No path found")

    # logger.debug(f"Found about.xml at {about_file.absolute()}")

    if not about_file.exists():
        logger.critical(f"Could not find about.xml for {str(path)}")
        raise OSError("No path found")

    async with async_open(about_file,"rb") as aboutxml:
        try:
            xml = xmltodict.parse((await aboutxml.read()), dict_constructor=dict)
            
            # Sometimes people capitalise ModMetaData weridly, so this just grabs the first element
            return xml[list(xml)[0]] 
        except ExpatError:
            logger.error(f"Expat error in "+str(about_file.absolute()))
            return {}

async def generate_mod_from_scratch(path: Path, mod_steam_info=None) -> Mod:
    def read_li(about: dict[Any, Any],atr: str) -> list[Union[str,dict]]:
        items: list[Union[str,dict]] = []
        if atr in about:
            if about[atr]:
                if about[atr]["li"]:
                    items = about[atr]["li"]

                    # If there's more than one li, then its already list, otherwise, make it a list.
                    items = [items] if isinstance(items,dict) or isinstance(items,str) else items
                else:
                    items = []
        else:
            items = []
        return items
    
    about = await mod_about(path)

    if "packageId" in about:
        pid = about["packageId"].lower()  
    else:
        raise Exception(f"Mod {path} has no pid")

    if pid.startswith("ludeon."):
        source = "LUDEON"
    elif mod_steam_info is not None:
        source = "STEAM"
        steam_info = await mod_steam_info
    elif (path / ".git").is_dir():
        source = "GIT"
    else:
        source = "LOCAL"

    name = about["name"] if "name" in about else pid
    author = about["author"] if "author" in about else ""

    if "url" in about:
        download_link = about["url"]
    elif source=="STEAM":
        download_link = f"https://steamcommunity.com/sharedfiles/filedetails/?id={path.name}"
    elif source=="GIT":
        subprocess.check_output(["git", "-C",path.as_posix(),"config", "--get", "remote.origin.url"]).decode("utf-8").rstrip()
    else:
        download_link=""

    deps = [dep["packageId"].lower() for dep in read_li(about, "modDependencies")] #type: ignore
    load_before = [dep.lower() for dep in read_li(about, "loadBefore")] # type: ignore
    load_after = [dep.lower() for dep in read_li(about, "loadAfter")] # type: ignore

    supported_versions = read_li(about, "supportedVersions")
    
    time_updated=time.time()
    time_first_downloaded=0


    if source == "STEAM":
        pfid = f"{steam_info["preview_url"]}?imw=100&imh=100&impolicy=Letterbox" if "preview_url" in steam_info else "https://github.com/RimSort/RimSort/blob/main/docs/rentry_steam_icon.png?raw=true"
        filesize = steam_info["file_size"] if "file_size" in steam_info else 0
    elif source == "LUDEON":
        pfid = "https://github.com/dormieriancitizen/rimworld_instance_manager/blob/main/resources/ludeon-studios.png?raw=true"
        filesize = 0
    elif source=="GIT":
        pfid="https://github.com/dormieriancitizen/rimworld_instance_manager/blob/main/resources/github-banner.png?raw=true"
        filesize=0
    elif source=="LOCAL":
        pfid = "https://github.com/dormieriancitizen/rimworld_instance_manager/blob/main/resources/local-banner.png?raw=true"
        filesize = 0

    return Mod(
        path=path,
        source=source,
        pid=pid,
        name=name,
        deps=deps,
        load_before=load_before,
        load_after=load_after,
        supported_versions=supported_versions, # type: ignore
        time_first_downloaded=time_first_downloaded,
        time_updated=time_updated,
        download_link=download_link,
        pfid=pfid,
        filesize=filesize
    )

async def generate_mod_from_cache(cached: Any) -> Mod:
    path = Path(cached["path"])
    source = cached["source"]

    pid = cached["pid"]
    name = cached["name"]

    deps = cached["deps"]
    load_before = cached["load_before"]
    load_after = cached["load_after"]

    supported_versions = cached["supported_versions"]

    time_first_downloaded = cached["time_first_downloaded"]
    time_updated = cached["time_updated"]

    download_link = cached["download_link"]

    pfid = cached["pfid"]
    filesize = cached["filesize"]
    
    return Mod(
        path=path,
        source=source,
        pid=pid,
        name=name,
        deps=deps,
        load_before=load_before,
        load_after=load_after,
        supported_versions=supported_versions,
        time_first_downloaded=time_first_downloaded,
        time_updated=time_updated,
        download_link=download_link,
        pfid=pfid,
        filesize=filesize
    )

def is_steam_mod(path: Path) -> bool:
    # fix later
    if not path.name.isnumeric():
        return False
    if not len(path.name) >= 9:
        return False
    if not len(path.name) <= 10:
        return False
    else:
        return True