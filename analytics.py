from datetime import date, timedelta
from db import get_all_habits, get_logs_for_habit, is_logged_today


def calculate_streak(logged_dates: list) -> dict:
    """
    Given a list of logged date strings, return:
    - current_streak: consecutive days ending today or yesterday
    - longest_streak: all-time best run
    """
    if not logged_dates:
        return {"current_streak": 0, "longest_streak": 0}

    # Convert to date objects and sort
    dates = sorted(set(date.fromisoformat(d) for d in logged_dates))

    # Longest streak
    longest = 1
    current_run = 1
    for i in range(1, len(dates)):
        if (dates[i] - dates[i - 1]).days == 1:
            current_run += 1
            longest = max(longest, current_run)
        else:
            current_run = 1

    # Current streak — must end today or yesterday to still be "alive"
    today = date.today()
    yesterday = today - timedelta(days=1)

    if dates[-1] not in (today, yesterday):
        current_streak = 0
    else:
        current_streak = 1
        for i in range(len(dates) - 2, -1, -1):
            if (dates[i + 1] - dates[i]).days == 1:
                current_streak += 1
            else:
                break

    return {"current_streak": current_streak, "longest_streak": longest}


def completion_rate(logged_dates: list, created_at: str, window_days: int = 30) -> float:
    """
    Percentage of days the habit was logged over the last `window_days` days
    (or since creation, whichever is shorter).
    """
    today = date.today()
    start = max(
        today - timedelta(days=window_days - 1),
        date.fromisoformat(created_at)
    )
    total_days = (today - start).days + 1

    if total_days == 0:
        return 0.0

    logged_set = set(date.fromisoformat(d) for d in logged_dates)
    logged_in_window = sum(1 for d in logged_set if start <= d <= today)

    return round((logged_in_window / total_days) * 100, 1)


def get_all_stats() -> list:
    """
    Return a list of dicts with full stats for every habit.
    Used by both CLI status and the dashboard.
    """
    habits = get_all_habits()
    stats = []

    for habit in habits:
        logs = get_logs_for_habit(habit["id"])
        streak_data = calculate_streak(logs)
        rate = completion_rate(logs, habit["created_at"])

        stats.append({
            "id": habit["id"],
            "name": habit["name"],
            "created_at": habit["created_at"],
            "logged_today": is_logged_today(habit["id"]),
            "total_logs": len(logs),
            "current_streak": streak_data["current_streak"],
            "longest_streak": streak_data["longest_streak"],
            "completion_rate_30d": rate,
            "logged_dates": logs,
        })

    return stats
