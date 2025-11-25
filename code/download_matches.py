import json
from pathlib import Path

from riotwatcher import RiotWatcher, LolWatcher, ApiError
from config import RIOT_API_KEY, LOL_PLATFORM_REGION, LOL_ROUTING_REGION
from utilities import load_puuid, dir_exists

GET_MATCHES_COUNT = 30  # Number of matches to fetch per request

# Directories and file paths
PUUID_FILE = Path(__file__).parent.parent / "puuid.txt"
DATA_DIR = Path(__file__).parent.parent / "data"
MATCHES_DIR = DATA_DIR / "matches"
TIMELINES_DIR = DATA_DIR / "timelines"


def main():
    if not RIOT_API_KEY:
        raise RuntimeError("RIOT_API_KEY not set. Please set it in the .env file.")
    
    puuid = load_puuid()
    dir_exists()
    
    lol = LolWatcher(RIOT_API_KEY)
    riot = RiotWatcher(RIOT_API_KEY)

    print("PUUID:", puuid)
    print("Routing Region:", LOL_ROUTING_REGION)
    print("Platform Region:", LOL_PLATFORM_REGION)

    # Fetch match IDs
    try:
        start_index = 0
        match_ids = lol.match.matchlist_by_puuid(LOL_PLATFORM_REGION, start=start_index, puuid=puuid, count=GET_MATCHES_COUNT)
        
    except ApiError as error:
        print("ApiError while fetching match IDs:")
        print("Status:", error.response.status_code)
        print("Body:  ", error.response.text)
        return

    print(f"Fetched {len(match_ids)} match IDs.")
    for m in match_ids:
        print(" -", m)

    # Fetch and save match details and timelines
    for m in match_ids:
        m_path = MATCHES_DIR / f"{m}.json"
        t_path = TIMELINES_DIR / f"{m}_timeline.json"

        # check if files already exist
        if m_path.exists() and t_path.exists():
            print(f"Match {m} already downloaded. Skipping.")
            continue

        print(f"Downloading match {m}...")

        # Fetch match details
        try:
            match_detail = lol.match.by_id(LOL_ROUTING_REGION, m)
        except ApiError as error:
            print(f"ApiError while fetching match details for {m}:")
            print("Status:", error.response.status_code)
            print("Body:  ", error.response.text)
            continue
        # Fetch timeline details
        try:
            match_timeline = lol.match.timeline_by_match(LOL_ROUTING_REGION, m)
        except ApiError as error:
            print(f"ApiError while fetching match timeline for {m}:")
            print("Status:", error.response.status_code)
            print("Body:  ", error.response.text)
            continue

        # Save to files
        with m_path.open("w", encoding="utf-8") as f:
            json.dump(match_detail, f, ensure_ascii=False, indent=2)
        with t_path.open("w", encoding="utf-8") as f:
            json.dump(match_timeline, f, ensure_ascii=False, indent=2)

        print(f"[DONE] Saved match {m} details and timeline.")

if __name__ == "__main__":
    main()