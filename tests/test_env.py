import os

from dotenv import load_dotenv
from riotwatcher import LolWatcher, RiotWatcher, ApiError


def main():
    load_dotenv()

    api_key = os.getenv("RIOT_API_KEY")
    if not api_key:
        raise RuntimeError("RIOT_API_KEY is not set in .env")

    game_name = os.getenv("RIOT_IGN")
    tag = os.getenv("RIOT_TAG")
    platform_region = os.getenv("LOL_PLATFORM_REGION")
    routing_region = os.getenv("LOL_ROUTING_REGION")

    print("API key present? ", bool(api_key))
    print(f"Riot ID: {game_name}#{tag}")
    print(f"Platform region: {platform_region}")
    print(f"Routing region:  {routing_region}")

    lol_watcher = LolWatcher(api_key)
    riot_watcher = RiotWatcher(api_key)

    try:
        # Dictionaries
        
        # 1) Get account info by Riot ID
        account = riot_watcher.account.by_riot_id(routing_region, game_name, tag)

        print("\nAccount data:")
        print(account)

        puuid = account["puuid"]
        print("\nPUUID:", puuid)

        # 2) Get summoner info by PUUID
        summoner = lol_watcher.summoner.by_puuid(platform_region, puuid)
        print("\nSummoner data:")
        print(summoner)

    except ApiError as e:
        print("\nApiError occurred:")
        print(f"Status code: {e.response.status_code}")
        print(f"Response:    {e.response.text}")


if __name__ == "__main__":
    main()
