from pathlib import Path

# Pathlib path

# Posix string
STEAMCMD_PATH = "/home/dormierian/Games/rimworld/SteamCMD/steamcmd.sh"

# Places to find mods
WORKSHOP_PATH = Path("/home/dormierian/.local/share/Steam/steamapps/workshop/content/294100/")
GITHUB_MODS_PATH = Path("/home/dormierian/Games/rimtag/github_mods")
LOCAL_MODS_PATH = Path("/home/dormierian/Games/rimtag/local_mods")
RIMWORLD_DATA_PATH = Path("/home/dormierian/Games/rimworld/Data/")


#List of paths
MOD_SCAN_DIRS = [
        RIMWORLD_DATA_PATH,
        WORKSHOP_PATH,
        LOCAL_MODS_PATH,
        GITHUB_MODS_PATH
    ]