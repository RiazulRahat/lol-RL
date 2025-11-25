import json
from pathlib import Path

from utilities import load_puuid, dir_exists

PUUID_FILE = DATA_DIR = Path(__file__).parent.parent / "puuid.txt"
DATA_DIR = DATA_DIR = Path(__file__).parent.parent / "data"
MATCHES_DIR = DATA_DIR / "matches"
TIMELINES_DIR = DATA_DIR / "timelines"
CLEAN_DIR = DATA_DIR / "clean_matches"

def is_summoners_rift(info):
    """Return True if the match is a summoners rift allowed game mode."""
    
    # Summoner's Rift map ID is 11
    if info.get("mapId") != 11:
        return False
    
    # Check classic game modes
    if info.get("gameMode") != "CLASSIC":
        return False
    
    # Queue IDs for Summoner's Rift
    # 400: Normal Draft
    # 420: Ranked Solo/Duo
    # 430: Normal Blind
    # 440: Ranked Flex

    allowed_queues = {400, 420, 430, 440}
    if info.get("queueId") not in allowed_queues:
        return False
    
    return True


def is_remake(info):
    """All games that end before 5 minutes are remakes."""

    # duration is in seconds
    duration = info.get("gameDuration", 0)

    return duration < 300


def player_data(info, puuid):
    """Return the player's data from the match info. None if not found."""
    
    for playerdata in info.get("participants", []):
        if playerdata.get("puuid") == puuid:
            return playerdata
    return None


# Role checkers
def is_jungle(playerdata):
    """Return True if player played jungle role."""

    position = playerdata.get("individualPosition") or playerdata.get("teamPosition")
    return position == "JUNGLE"

def is_mid(playerdata):
    """Return True if player played mid role."""

    position = playerdata.get("individualPosition") or playerdata.get("teamPosition")
    return position == "MIDDLE"

def is_top(playerdata):
    """Return True if player played top role."""

    position = playerdata.get("individualPosition") or playerdata.get("teamPosition")
    return position == "TOP"

def is_adc(playerdata):
    """Return True if player played ADC role."""

    position = playerdata.get("individualPosition") or playerdata.get("teamPosition")
    return position == "BOTTOM" and playerdata.get("role") == "DUO_CARRY"

def is_support(playerdata):
    """Return True if player played support role."""

    position = playerdata.get("individualPosition") or playerdata.get("teamPosition")
    return position == "BOTTOM" and playerdata.get("role") == "DUO_SUPPORT"


# Create clean data files
def build_clean_data():
    dir_exists()

    puuid = load_puuid()
    print("Loaded PUUID:", puuid)

    # Check if matches directory exists
    if not MATCHES_DIR.exists():
        raise RuntimeError(f"{MATCHES_DIR} does not exist. Run download_matches.py first.")
    
    data = []

    match_files = sorted(MATCHES_DIR.glob("*.json"))
    print(f"Found {len(match_files)} raw match files")

    for m_path in match_files:
        # Load match data
        with m_path.open("r", encoding="utf-8") as f:
            match = json.load(f)
        
        metadata = match.get("metadata", {})
        info = match.get("info", {})

        m_id = metadata.get("matchId", m_path.stem)

        # Corresponding timeline file
        t_path = TIMELINES_DIR / f"{m_id}_timeline.json"
        if not t_path.exists():
            print("No timeline for match", m_id, "Skipping...")
            continue

        # Filter checks
        if not is_summoners_rift(info):
            print("Match", m_id, "is not Summoner's Rift or allowed game mode. Skipping...")
            continue
        
        if is_remake(info):
            print("Match", m_id, "is a remake. Skipping...")
            continue

        me = player_data(info, puuid)
        if me is None:
            print("Could not find player data for match", m_id, "Skipping...")
            continue

        if not is_top(me):
            print(f"Player did not play top in match, (teamPosition={me.get('teamPosition')})", m_id, "Skipping...")
            continue


        # Build a summary report

        # Calculate CS
        cs = (me.get("totalMinionsKilled", 0) or 0) + (me.get("neutralMinionsKilled", 0) or 0)

        entry = {
            "matchId": m_id,
            "gameCreation": info.get("gameCreation"),   # timestamp in ms
            "gameDuration": info.get("gameDuration"),   # duration in seconds
            "queueId": info.get("queueId"),
            "mapId": info.get("mapId"),
            "gameMode": info.get("gameMode"),
            "championName": me.get("championName"),
            "teamposition": me.get("teamPosition") or me.get("individualPosition"),
            "win": bool(me.get("win")),                 # convert to bool
            "kills": me.get("kills"),
            "deaths": me.get("deaths"),
            "assists": me.get("assists"),
            "cs": cs,
            "jungleMinionsKilled": me.get("neutralMinionsKilled"),
        }

        data.append(entry)

    # Save clean data to file
    clean_path = CLEAN_DIR / "top_matches_index.json"
    with clean_path.open("w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Saved {len(data)} clean top match entries to {clean_path}")


def main():
    build_clean_data()

if __name__ == "__main__":
    main()