
import os
from dotenv import load_dotenv

# Load variables from .env file when this module is imported
load_dotenv()

RIOT_API_KEY = os.getenv("RIOT_API_KEY")
RIOT_IGN = os.getenv("RIOT_IGN")
RIOT_TAG = os.getenv("RIOT_TAG")

LOL_PLATFORM_REGION = os.getenv("LOL_PLATFORM_REGION", "na1")
LOL_ROUTING_REGION = os.getenv("LOL_ROUTING_REGION", "americas")


def check_config():
    print("RIOT_API_KEY set?   ", "Yes" if RIOT_API_KEY else "No")
    print("RIOT_IGN:           ", RIOT_IGN)
    print("RIOT_TAG:           ", RIOT_TAG)
    print("LOL_PLATFORM_REGION:", LOL_PLATFORM_REGION)
    print("LOL_ROUTING_REGION: ", LOL_ROUTING_REGION)
