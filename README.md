# 🔥 Habit Streak Tracker

A dual-interface habit tracker — log from the terminal, visualize in the browser.

![Dashboard Preview](assets/dashboard.png)

## Features

- **CLI** — add habits, log completions, view status with colour-coded streaks
- **Streamlit Dashboard** — GitHub-style heatmap, completion bar chart, streak stats
- **Streak logic** — current streak, longest streak, 30-day completion rate
- **SQLite backend** — zero-config, everything lives in a local `.db` file
- **Clean architecture** — `db.py` and `analytics.py` are shared by both interfaces

## Setup

```bash
git clone https://github.com/yourusername/habit-tracker
cd habit-tracker
pip install -r requirements.txt
```

## CLI Usage

```bash
# Add a habit
python habit.py add "Read 30 mins"
python habit.py add "Gym"
python habit.py add "No phone before 9am"

# Log a habit (mark as done today)
python habit.py log "Read 30 mins"

# Log for a specific date
python habit.py log "Gym" --date 2026-05-15

# Undo a log
python habit.py unlog "Gym"

# View all habits and streaks
python habit.py status

# Delete a habit
python habit.py delete "Read 30 mins"
```

### Status output example

```
Habit                        Today   Streak   Best   30d%
──────────────────────────────────────────────────────────
Gym                            ✓      14d      21d   80.0%
Read 30 mins                   ✓       7d       7d   66.7%
No phone before 9am            ✗       2d       5d   43.3%

  2/3 habits done today.
```

## Dashboard

```bash
streamlit run dashboard.py
```

Opens at `http://localhost:8501`

**Pages:**
- Overview metrics (done today, best streak, avg completion)
- Habit list with streak pills
- GitHub-style 52-week heatmap per habit
- 30-day completion bar chart

## Project Structure

```
habit-tracker/
├── habit.py          # CLI entry point (argparse)
├── dashboard.py      # Streamlit dashboard
├── db.py             # SQLite — all reads and writes
├── analytics.py      # Streak and completion logic
├── data/
│   └── habits.db     # Auto-created on first run
├── requirements.txt
└── README.md
```

## Tech Stack

| Layer       | Tool           |
|-------------|----------------|
| Database    | SQLite (stdlib)|
| CLI         | argparse       |
| Dashboard   | Streamlit      |
| Charts      | Plotly         |
| Data        | pandas         |

## Deploy (optional)

Push to GitHub, then deploy the dashboard free on [Streamlit Cloud](https://streamlit.io/cloud).
Connect your repo, set `dashboard.py` as the entry point — done.

---

Built as a portfolio project to demonstrate: CLI design, SQLite schema design, data visualization, and clean module separation.
