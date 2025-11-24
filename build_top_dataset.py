import os
import json
import math
import csv
from pathlib import Path

from dotenv import load_dotenv
from utilities import load_puuid, dir_exists, load_json

load_dotenv()

DATA_DIR = Path("data")
MATCHES_DIR = DATA_DIR / "matches"
TIMELINES_DIR = DATA_DIR / "timelines"
CLEAN_DIR = DATA_DIR / "clean_matches"
TOP_INDEX_FILE = CLEAN_DIR / "top_matches_index.json"
OUTPUT_CSV = DATA_DIR / "datasets" /"top_matches_summary.csv"

my_puuid = load_puuid()

LANE_PHASE_MAX_TIME = 20 * 60  # 20 mins



def get_top_laners(match, my_puuid):
    """
    Parameters:
        - match: match JSON data
        - my_puuid: my PUUID string

    Return:
        - my participant ID
        - enemy top laner's participant ID
        - my side (BLUE/RED)
    """

    metadata = match["metadata"]
    info = match["info"]

    puuids = metadata["participants"]
    participants = info["participants"]

    # find my champion
    try:
        my_index = puuids.index(my_puuid)
    except ValueError:
        print("My PUUID not found in match participants.")

    # find my participant details
    my_participant = participants[my_index]
    my_pid = my_participant["participantId"]
    my_team_id = my_participant["teamId"]
    my_side = "BLUE" if my_team_id == 100 else "RED"

    # find enemy top laner
    enemy_top = None
    for p in participants:
        if p["teamId"] != my_team_id and p["individualPosition"] == "TOP":
            enemy_top = p
            break
    
    # if enemy top laner not found compare with best enemy laner in terms of CS
    if enemy_top is None:
        players = [p for p in participants if p["teamId"] != my_team_id]
        enemy_top = max(players, key=lambda p: p.get("totalMinionsKilled", 0))
    
    enemy_pid = enemy_top["participantId"]

    return my_pid, enemy_pid, my_side


def lane_end_time(timeline):
    """
    Parameters:
        - timeline: timeline JSON data
    
    Return:
        - time (in seconds) when top lane outer turret is destroyed
          or LANE_PHASE_MAX_TIME if not destroyed within that time
    """
    lane_end = LANE_PHASE_MAX_TIME
    frames = timeline["info"]["frames"]

    for frame in frames:
        for event in frame.get("events", []):
            if event.get("type") == "BUILDING_KILL":
                lane_type = event.get("laneType")
                tower_type = event.get("towerType")
                if lane_type == "TOP_LANE" and tower_type == "OUTER_TURRET":
                    time_s = event["timestamp"] / 1000
                    lane_end = min(lane_end, time_s)
                    return lane_end
                
    return lane_end


def dist_from_base(position, side):

    """
    Parameters:
        - position: dict with 'x' and 'y' coordinates
        - side: "BLUE" or "RED"
    
    Return:
        - Euclidean distance from base
    """
    x, y = position["x"], position["y"]
    if side == "BLUE":
        base_x, base_y = 0, 0
    else:
        base_x, base_y = 16000, 16000
    
    return math.sqrt((x - base_x) ** 2 + (y - base_y) ** 2)


def process_match(match_id):
    """Generate data snapshots for a single top lane match."""
    match_path = MATCHES_DIR / f"{match_id}.json"
    timeline_path = TIMELINES_DIR / f"{match_id}_timeline.json"

    if not match_path.exists():
        print(f"Match file missing for {match_id}, Skipping...")
        return []

    if not timeline_path.exists():
        print(f"Timeline file missing for {match_id}, Skipping...")
        return []
    
    match = load_json(match_path)
    timeline = load_json(timeline_path)

    try:
        my_pid, enemy_pid, my_side = get_top_laners(match, my_puuid)
    except Exception as error:
        print(f"Error in match {match_id}: {error}")
        return []
    
    frames = timeline["info"]["frames"]
    if not frames:
        print(f"No frames in timeline for match {match_id}, Skipping...")
        return []
    
    lane_time = lane_end_time(timeline)
    
    valid_frame_indices = [i for i, frame in enumerate(frames) if frame["timestamp"] / 1000 <= lane_time]
    if not valid_frame_indices:
        print(f"No valid frames within lane phase for match {match_id}, Skipping...")
        return []
    
    final_index = max(valid_frame_indices)
    final_frame = frames[final_index]
    final_pf_self = final_frame["participantFrames"][str(my_pid)]
    final_pf_enemy = final_frame["participantFrames"][str(enemy_pid)]

    final_cs_self = final_pf_self["minionsKilled"] + final_pf_self["jungleMinionsKilled"]
    final_cs_enemy = final_pf_enemy["minionsKilled"] + final_pf_enemy["jungleMinionsKilled"]
    final_cs_diff = final_cs_self - final_cs_enemy

    # Determine if ahead or behind in CS
    is_ahead = 1 if final_cs_diff > 0 else 0

    snapshots = []
    for frame in frames[:final_index+1]:
        time_s = frame["timestamp"] / 1000

        pf_self = frame["participantFrames"][str(my_pid)]
        pf_enemy = frame["participantFrames"][str(enemy_pid)]

        position_self = pf_self.get("position")
        position_enemy = pf_enemy.get("position")
        if not position_self or not position_enemy:
            continue

        cs_self = pf_self["minionsKilled"] + pf_self["jungleMinionsKilled"]
        cs_enemy = pf_enemy["minionsKilled"] + pf_enemy["jungleMinionsKilled"]
        
        xp_self = pf_self["xp"]
        xp_enemy = pf_enemy["xp"]

        # differences in champ positions both laners
        dist_x = position_self["x"] - position_enemy["x"]
        dist_y = position_self["y"] - position_enemy["y"]
        distance = math.sqrt(dist_x ** 2 + dist_y ** 2)

        base_dist_self = dist_from_base(position_self, my_side)

        snapshot = {
            "match_id": match_id,
            "time_s": time_s,

            "cs_self": cs_self,
            "cs_enemy": cs_enemy,
            "cs_diff": cs_self - cs_enemy,

            "xp_self": xp_self,
            "xp_enemy": xp_enemy,
            "xp_diff": xp_self - xp_enemy,

            "self_x": position_self["x"],
            "self_y": position_self["y"],
            "enemy_x": position_enemy["x"],
            "enemy_y": position_enemy["y"],
            "champ_distance": distance,
            "self_base_distance": base_dist_self,

            "cs_diff_final": final_cs_diff,
            "is_ahead_final": is_ahead
        }
        snapshots.append(snapshot)

    return snapshots


def main():
    if not TOP_INDEX_FILE.exists():
        raise FileNotFoundError(f"Top index not found at {TOP_INDEX_FILE}")
    
    index = load_json(TOP_INDEX_FILE)
    
    all_rows = []
    for entry in index:

        match_id = entry.get("matchId")
        if not match_id:
            continue

        rows = process_match(match_id)
        all_rows.extend(rows)

    if not all_rows:
        print("No snapshots generated. Check paths/index/puuid.")
        return
    
    fieldnames = list(all_rows[0].keys())

    OUTPUT_CSV.parent.mkdir(parents=True, exist_ok=True)
    with OUTPUT_CSV.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Wrote {len(all_rows)} snapshots to {OUTPUT_CSV}")

if __name__ == "__main__":
    main()