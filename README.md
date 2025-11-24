Working with Riot Games API and Game Data using RiotWatcher wrapper

# LoL

Vision: Offline reinforcement-learning / neural network project that analyzes my
League of Legends games from replays (match + timeline data) and
makes post-game recommendations.



## Current status

- Riot API integration:
  - Get PUUID from Riot ID
  - Download recent matches and timelines
  - Separate played lane info into separate json files
  - Create a CSV file with training dataset using snapshots from all available data

- Data stored locally in `data/` (ignored by git)
