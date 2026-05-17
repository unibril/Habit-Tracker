import argparse
import sys
from datetime import date

from db import init_db, add_habit, delete_habit, log_habit, unlog_habit, get_habit_by_name
from analytics import get_all_stats


# ── Colours ──────────────────────────────────────────────────────────────────
GREEN  = "\033[92m"
YELLOW = "\033[93m"
RED    = "\033[91m"
CYAN   = "\033[96m"
BOLD   = "\033[1m"
RESET  = "\033[0m"

def ok(msg):    print(f"{GREEN}✓ {msg}{RESET}")
def warn(msg):  print(f"{YELLOW}⚠ {msg}{RESET}")
def err(msg):   print(f"{RED}✗ {msg}{RESET}")
def info(msg):  print(f"{CYAN}{msg}{RESET}")


# ── Handlers ──────────────────────────────────────────────────────────────────

def cmd_add(args):
    name = " ".join(args.name)
    if add_habit(name):
        ok(f"Habit added: '{name}'")
    else:
        warn(f"Habit '{name}' already exists.")


def cmd_delete(args):
    name = " ".join(args.name)
    habit = get_habit_by_name(name)
    if not habit:
        err(f"No habit named '{name}' found.")
        return
    confirm = input(f"Delete '{name}' and all its logs? [y/N]: ").strip().lower()
    if confirm == "y":
        delete_habit(name)
        ok(f"Deleted '{name}'.")
    else:
        info("Cancelled.")


def cmd_log(args):
    name = " ".join(args.name)
    log_date = date.fromisoformat(args.date) if args.date else date.today()
    result = log_habit(name, log_date)

    if result == "ok":
        ok(f"Logged '{name}' for {log_date}. Keep it up!")
    elif result == "already_logged":
        warn(f"'{name}' already logged for {log_date}.")
    elif result == "not_found":
        err(f"No habit named '{name}'. Use 'add' first.")


def cmd_unlog(args):
    name = " ".join(args.name)
    log_date = date.fromisoformat(args.date) if args.date else date.today()
    if unlog_habit(name, log_date):
        ok(f"Removed log for '{name}' on {log_date}.")
    else:
        err(f"No habit named '{name}' found.")


def cmd_status(args):
    stats = get_all_stats()

    if not stats:
        info("No habits yet. Add one with: python habit.py add \"Your habit\"")
        return

    print(f"\n{BOLD}{'Habit':<28} {'Today':>6} {'Streak':>8} {'Best':>6} {'30d%':>6}{RESET}")
    print("─" * 58)

    for s in stats:
        logged = f"{GREEN}✓{RESET}" if s["logged_today"] else f"{RED}✗{RESET}"
        streak = f"{s['current_streak']}d"
        best   = f"{s['longest_streak']}d"
        rate   = f"{s['completion_rate_30d']}%"
        name   = s["name"][:27]  # truncate long names

        # Colour-code the streak
        streak_col = GREEN if s["current_streak"] >= 7 else YELLOW if s["current_streak"] >= 3 else RESET
        print(
            f"{name:<28} {logged:>6}  "
            f"{streak_col}{streak:>7}{RESET}  {best:>6}  {rate:>6}"
        )

    print()
    total_today = sum(1 for s in stats if s["logged_today"])
    print(f"  {BOLD}{total_today}/{len(stats)} habits done today.{RESET}\n")


# ── Main ──────────────────────────────────────────────────────────────────────

def main():
    init_db()

    parser = argparse.ArgumentParser(
        prog="habit",
        description="Habit Streak Tracker — log habits from the terminal.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python habit.py add "Read 30 mins"
  python habit.py log "Read 30 mins"
  python habit.py log "Read 30 mins" --date 2026-05-15
  python habit.py unlog "Read 30 mins"
  python habit.py status
  python habit.py delete "Read 30 mins"
        """
    )

    subparsers = parser.add_subparsers(dest="command", metavar="command")
    subparsers.required = True

    # add
    p_add = subparsers.add_parser("add", help="Add a new habit")
    p_add.add_argument("name", nargs="+", help="Habit name (wrap in quotes)")
    p_add.set_defaults(func=cmd_add)

    # delete
    p_del = subparsers.add_parser("delete", help="Delete a habit and all its logs")
    p_del.add_argument("name", nargs="+", help="Habit name")
    p_del.set_defaults(func=cmd_delete)

    # log
    p_log = subparsers.add_parser("log", help="Mark a habit as done")
    p_log.add_argument("name", nargs="+", help="Habit name")
    p_log.add_argument("--date", help="Date to log (YYYY-MM-DD), default: today")
    p_log.set_defaults(func=cmd_log)

    # unlog
    p_unlog = subparsers.add_parser("unlog", help="Remove a log entry")
    p_unlog.add_argument("name", nargs="+", help="Habit name")
    p_unlog.add_argument("--date", help="Date to unlog (YYYY-MM-DD), default: today")
    p_unlog.set_defaults(func=cmd_unlog)

    # status
    p_status = subparsers.add_parser("status", help="Show all habits and their streaks")
    p_status.set_defaults(func=cmd_status)

    args = parser.parse_args()
    args.func(args)


if __name__ == "__main__":
    main()
