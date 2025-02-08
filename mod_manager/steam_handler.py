from typing import Any
import logging, aiohttp

from pathlib import Path

from config import CONFIG_PATH
from mod_manager.cache import update_json_cache

async def fetch_from_steam(steam_ids: list[str]) -> dict[str, dict[str, Any]]:
    logger = logging.getLogger()

    logger.debug(f"Fetching details for {len(steam_ids)} Steam IDs")

    url = "https://api.steampowered.com/ISteamRemoteStorage/GetPublishedFileDetails/v1/"

    payload: dict[str,Any] = {"itemcount": len(steam_ids)}

    for i, steam_id in enumerate(steam_ids):
        payload[f"publishedfileids[{i}]"] = str(steam_id)

    async with aiohttp.ClientSession() as session:
        async with session.post(url, data=payload) as response:
            if response.status != 200:
                logger.error(f"Received non-200 response code: {response.status}")
                return {}
            try:
                data = await response.json()
                published_file_details = data.get("response", {}).get("publishedfiledetails", [])
            except Exception as e:
                print(f"Error parsing response: {e}")
                return {}

    steamd = {file_detail["publishedfileid"]: file_detail for file_detail in published_file_details}

    cache_path = (CONFIG_PATH / "steam_workshop_info.json")
    await update_json_cache(cache_path,steamd)

    logger.info(f"Fetched steam data")

    return steamd

async def mod_steam_info(path: Path, steam_source) -> dict[str, Any]:
    steamd: Any = await steam_source
    
    return steamd[path.name]