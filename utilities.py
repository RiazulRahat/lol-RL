from pathlib import Path
import json

# Directories and file paths
PUUID_FILE = Path("puuid.txt")
DATA_DIR = Path("data")
MATCHES_DIR = DATA_DIR / "matches"
TIMELINES_DIR = DATA_DIR / "timelines"


def load_puuid():
    """Load the player's PUUID from puuid.txt."""
    if not PUUID_FILE.exists():
        raise RuntimeError(f"{PUUID_FILE} not found. Run get_puuid.py first to generate it.")
    
    return PUUID_FILE.read_text(encoding="utf-8").strip()

def dir_exists():
    MATCHES_DIR.mkdir(parents=True, exist_ok=True)
    TIMELINES_DIR.mkdir(parents=True, exist_ok=True)

def load_json(path):
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)