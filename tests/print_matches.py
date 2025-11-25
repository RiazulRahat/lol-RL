import json
from pathlib import Path


INDEX_PATH = Path("data/clean_matches/jungle_matches_index.json")

def main():
    if not INDEX_PATH.exists():
        raise RuntimeError("Index file not found. Run clean_matches.py first.")

    data = json.loads(INDEX_PATH.read_text(encoding="utf-8"))

    print(f"Found {len(data)} jungler matches in index.\n")
    for m in data:
        print(
            f"{m['matchId']} | {m['championName']} | "
            f"KDA: {m['kills']}/{m['deaths']}/{m['assists']} | "
            f"{'WIN' if m['win'] else 'LOSS'}"
        )

if __name__ == "__main__":
    main()
