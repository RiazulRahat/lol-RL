# LoL


This project uses the Riot Games API (via RiotWatcher) and match/timeline data to build an offline ML / RL “coach” for League of Legends, focused on the early top-lane laning phase.

The idea is to analyze my own games, learn lane heuristics from data (CS, XP, positioning, etc.), and eventually give post-game feedback like “you were too aggressive here” or “you could safely pressure more here.”


Vision: Offline reinforcement-learning / neural network project that analyzes my
League of Legends games from replays (match + timeline data) and
makes post-game recommendations.


## Current status

- Riot API integration:
  - Resolve PUUID from Riot ID.
  - Download recent matches and timelines.
- Top lane filtering:
  - Identify games where I played top.
  - Build a top_matches index.
- Dataset:
  - Convert match + timeline JSON into per-minute lane snapshots.
  - Compute features like:
    - cs_self, cs_enemy, cs_diff
    - xp_self, xp_enemy, xp_diff
    - self_x / self_y, enemy_x / enemy_y
    - champ_distance
    - self_base_distance (for overextension)
    - time_s (seconds into game)
  - Label lane outcome:
    - cs_diff_final
    - is_ahead_final (1 if I end lane ahead in CS)
  - Store snapshots in a small CSV:
    - `data/datasets/top_matches_summary.csv` (versioned in git)


## Run

- can run notebook (top_lane_laning_model.ipynb) with the provided dataset
- or use codes on your own games
