from riotwatcher import RiotWatcher, ApiError
from code.config import RIOT_API_KEY, RIOT_IGN, RIOT_TAG, LOL_PLATFORM_REGION, LOL_ROUTING_REGION

def main():

    # check if config variables are set
    if not RIOT_API_KEY:
        raise RuntimeError("Riot API key is not set in .env")
    
    if not RIOT_IGN or not RIOT_TAG:
        raise RuntimeError("Riot IGN or TAG is not set in .env")
    
    riot = RiotWatcher(RIOT_API_KEY)

    # Get account info by Riot ID
    try:
        account = riot.account.by_riot_id(LOL_ROUTING_REGION, RIOT_IGN, RIOT_TAG)
    
    except ApiError as error:
        print("API Error: Could not fetch account information.")
        print("Status code:", error.response.status_code)
        print("Body:", error.response.text)
        return
    
    # Extract and print PUUID
    puuid = account["puuid"]
    print("PUUID:", puuid)

    # Save PUUID to a text file
    with open("puuid.txt", "w") as f:
        f.write(puuid)
    
    print("PUUID saved to puuid.txt")


if __name__ == "__main__":
    main()