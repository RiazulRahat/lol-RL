
from pathlib import Path
import pandas as pd


DATA_DIR = Path(__file__).parent.parent / "data"

# Input and output file paths
UNLABELED = DATA_DIR / "datasets" / "top_matches_summary.csv"
LABELED = DATA_DIR / "datasets" / "top_matches_labeled.csv"


THRESHOLD = 1000
CHAMP_MIN_DIST = 6000
BASE_MIN_DIST = 5000

def main():
    if not UNLABELED.exists():
        raise FileNotFoundError(f"Input file {UNLABELED} does not exist.")
    
    data = pd.read_csv(UNLABELED)
    print(f"Loaded dataset", data.shape)

    data = data.sort_values(["match_id", "time_s"]).reset_index(drop=True)

    # Create columns with next step values
    next_mid = data["match_id"].shift(-1)
    next_sbd = data["self_base_distance"].shift(-1)
    next_cd = data["champ_distance"].shift(-1)

    # Boolean to check same match next step
    same_match = (data["match_id"] == next_mid)

    # Calculate changes between current and next step
    delta_sbd = next_sbd - data["self_base_distance"]
    delta_cd = next_cd - data["champ_distance"]

    # Placeholder for labels
    data["label"] = "NEUTRAL"

    # AGGRESSIVE: same match, self_base_distance increases by THRESHOLD, champ_distance decreases, champ_distance < CHAMP_MIN_DIST
    mark_aggressive = (
        same_match & (delta_sbd > THRESHOLD) & (delta_cd < 0) & ((data["champ_distance"] < CHAMP_MIN_DIST) & (data["self_base_distance"] > BASE_MIN_DIST))
    )

    # SAFE: same match, self_base_distance decreases by THRESHOLD, champ_distance increases, champ_distance < CHAMP_MIN_DIST
    mark_safe = (
        same_match & (delta_sbd < -THRESHOLD) & (delta_cd >= 0) & ((data["champ_distance"] < CHAMP_MIN_DIST) & (data["self_base_distance"] > BASE_MIN_DIST))
    )

    data.loc[mark_aggressive, "label"] = "AGGRESSIVE"
    data.loc[mark_safe, "label"] = "SAFE"

    data.to_csv(LABELED, index=False)
    print("Saved labeled dataset to", LABELED)


if __name__ == "__main__":
    main()


