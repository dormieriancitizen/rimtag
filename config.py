from pathlib import Path

# Path to rimworld config
RIMWORLD_CONFIG_PATH = Path("/home/dormierian/.config/unity3d/Ludeon Studios/RimWorld by Ludeon Studios/")
RIMWORLD_GAME_PATH = Path("/home/dormierian/Games/rimworld")

# Posix string
STEAMCMD_PATH = "/home/dormierian/Games/rimworld/SteamCMD/steamcmd.sh"

# Places to find mods
WORKSHOP_PATH = Path("/home/dormierian/.local/share/Steam/steamapps/workshop/content/294100/")
GITHUB_MODS_PATH = Path("/home/dormierian/Games/rimtag/github_mods")
LOCAL_MODS_PATH = Path("/home/dormierian/Games/rimtag/local_mods")
RIMWORLD_DATA_PATH = RIMWORLD_GAME_PATH / "Data"

#List of paths
MOD_SCAN_DIRS = [
        RIMWORLD_DATA_PATH,
        WORKSHOP_PATH,
        LOCAL_MODS_PATH,
        GITHUB_MODS_PATH
    ]

# Mod config
TIER_THREE_MODS = ["krkr.rocketman", "taranchuk.performanceoptimizer"]
DLC_NAMES = ["ludeon.ideology","ludeon.anomaly","ludeon.biotech","ludeon.royalty"]