import asyncio
from mod_manager.download_handler import steam_download_workshop_ids, github_download_links, process_downloads

mods = [
    "https://github.com/Taranchuk/FasterGameLoading",
    "https://github.com/Taranchuk/StartupProfiler",
    "https://github.com/bbradson/Performance-Fish",
    "https://github.com/bbradson/Fishery",
    "https://github.com/Vanilla-Expanded/VanillaQuestsExpanded-TheGenerator/",
]

steam_ids = [
    "3347026598",

]

# steam_download_workshop_ids(steam_ids)
async def main():
    await process_downloads(github_download_links(mods))
