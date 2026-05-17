import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import date, timedelta

from db import init_db, add_habit, delete_habit, log_habit, unlog_habit, get_all_habits
from analytics import get_all_stats

# ── Page config ───────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Habit Tracker",
    page_icon="🔥",
    layout="wide",
    initial_sidebar_state="expanded",
)

init_db()

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
    @import url('https://fonts.googleapis.com/css2?family=JetBrains+Mono:wght@400;700&family=Sora:wght@300;600;800&display=swap');

    html, body, [class*="css"] { font-family: 'Sora', sans-serif; }
    code, pre { font-family: 'JetBrains Mono', monospace; }

    .metric-card {
        background: #0f0f0f;
        border: 1px solid #2a2a2a;
        border-radius: 12px;
        padding: 1.2rem 1.5rem;
        text-align: center;
    }
    .metric-label { color: #666; font-size: 0.75rem; letter-spacing: 0.1em; text-transform: uppercase; }
    .metric-value { color: #f0f0f0; font-size: 2rem; font-weight: 800; margin: 0.2rem 0; }
    .metric-sub   { color: #888; font-size: 0.8rem; }

    .habit-row {
        display: flex; align-items: center; justify-content: space-between;
        background: #111; border: 1px solid #222; border-radius: 10px;
        padding: 0.8rem 1.2rem; margin-bottom: 0.5rem;
    }
    .habit-name  { font-weight: 600; font-size: 1rem; color: #eee; }
    .streak-pill {
        background: #1a1a1a; border-radius: 999px;
        padding: 0.2rem 0.8rem; font-size: 0.8rem;
        color: #f59e0b; font-family: 'JetBrains Mono', monospace;
    }
    .done-badge  { color: #22c55e; font-size: 1.2rem; }
    .miss-badge  { color: #ef4444; font-size: 1.2rem; }

    [data-testid="stSidebar"] { background: #0a0a0a; border-right: 1px solid #1e1e1e; }
    h1, h2, h3 { font-family: 'Sora', sans-serif; font-weight: 800; }
</style>
""", unsafe_allow_html=True)


# ── Sidebar ───────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🔥 Habit Tracker")
    st.markdown("---")

    # Add habit
    st.markdown("**Add a new habit**")
    new_habit = st.text_input("", placeholder="e.g. Read 30 mins", label_visibility="collapsed")
    if st.button("Add Habit", use_container_width=True):
        if new_habit.strip():
            if add_habit(new_habit.strip()):
                st.success(f"Added: {new_habit.strip()}")
                st.rerun()
            else:
                st.warning("Habit already exists.")
        else:
            st.warning("Enter a habit name.")

    st.markdown("---")

    # Log / unlog today
    st.markdown("**Log today**")
    habits = get_all_habits()
    if habits:
        habit_names = [h["name"] for h in habits]
        selected = st.selectbox("", habit_names, label_visibility="collapsed")
        col1, col2 = st.columns(2)
        with col1:
            if st.button("✓ Done", use_container_width=True):
                result = log_habit(selected)
                if result == "ok":
                    st.success("Logged!")
                elif result == "already_logged":
                    st.info("Already logged today.")
                st.rerun()
        with col2:
            if st.button("✗ Undo", use_container_width=True):
                unlog_habit(selected)
                st.info("Unlogged.")
                st.rerun()

    st.markdown("---")

    # Delete habit
    st.markdown("**Delete a habit**")
    if habits:
        del_name = st.selectbox("", habit_names, key="del_select", label_visibility="collapsed")
        if st.button("Delete", use_container_width=True, type="secondary"):
            delete_habit(del_name)
            st.success(f"Deleted '{del_name}'")
            st.rerun()


# ── Main ──────────────────────────────────────────────────────────────────────
stats = get_all_stats()

if not stats:
    st.markdown("# No habits yet.")
    st.markdown("Add your first habit in the sidebar →")
    st.stop()

# ── Top metrics ───────────────────────────────────────────────────────────────
st.markdown("# Today's Overview")

total = len(stats)
done_today = sum(1 for s in stats if s["logged_today"])
best_streak = max(s["current_streak"] for s in stats)
avg_rate = round(sum(s["completion_rate_30d"] for s in stats) / total, 1)

c1, c2, c3, c4 = st.columns(4)
for col, label, value, sub in [
    (c1, "Done Today",       f"{done_today}/{total}", "habits completed"),
    (c2, "Best Streak",      f"{best_streak}d",        "days in a row"),
    (c3, "Avg Completion",   f"{avg_rate}%",            "last 30 days"),
    (c4, "Total Habits",     str(total),                "being tracked"),
]:
    with col:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-label">{label}</div>
            <div class="metric-value">{value}</div>
            <div class="metric-sub">{sub}</div>
        </div>
        """, unsafe_allow_html=True)

st.markdown("---")

# ── Habit list ────────────────────────────────────────────────────────────────
st.markdown("### Habits")

for s in sorted(stats, key=lambda x: x["current_streak"], reverse=True):
    badge = "✓" if s["logged_today"] else "✗"
    badge_class = "done-badge" if s["logged_today"] else "miss-badge"
    fire = "🔥" if s["current_streak"] >= 7 else ""
    st.markdown(f"""
    <div class="habit-row">
        <span class="habit-name">{s['name']} {fire}</span>
        <span class="streak-pill">🔥 {s['current_streak']}d streak &nbsp;|&nbsp; best {s['longest_streak']}d &nbsp;|&nbsp; {s['completion_rate_30d']}%</span>
        <span class="{badge_class}">{badge}</span>
    </div>
    """, unsafe_allow_html=True)

st.markdown("---")

# ── Heatmap (GitHub-style) ────────────────────────────────────────────────────
st.markdown("### Streak Heatmap")

selected_habit = st.selectbox(
    "Select habit to view heatmap",
    [s["name"] for s in stats]
)

habit_data = next(s for s in stats if s["name"] == selected_habit)
logged_dates = set(habit_data["logged_dates"])

# Build 52-week grid
today = date.today()
start = today - timedelta(weeks=52)
# Align to Monday
start -= timedelta(days=start.weekday())

all_dates = [start + timedelta(days=i) for i in range((today - start).days + 1)]

# Build z matrix: 7 rows (days of week) x 53 cols (weeks)
weeks = {}
for d in all_dates:
    week_num = (d - start).days // 7
    dow = d.weekday()  # 0=Mon, 6=Sun
    weeks.setdefault(week_num, {})[dow] = {
        "date": d.isoformat(),
        "logged": d.isoformat() in logged_dates
    }

num_weeks = max(weeks.keys()) + 1
z = [[None] * num_weeks for _ in range(7)]
text = [[""] * num_weeks for _ in range(7)]

for week_num, days in weeks.items():
    for dow, info in days.items():
        z[dow][week_num] = 1 if info["logged"] else 0
        text[dow][week_num] = info["date"]

day_labels = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]

fig = go.Figure(go.Heatmap(
    z=z,
    text=text,
    hovertemplate="%{text}<extra></extra>",
    colorscale=[[0, "#1a1a1a"], [1, "#22c55e"]],
    showscale=False,
    xgap=3,
    ygap=3,
))

fig.update_layout(
    height=180,
    margin=dict(l=40, r=10, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    yaxis=dict(
        tickmode="array",
        tickvals=list(range(7)),
        ticktext=day_labels,
        autorange="reversed",
        tickfont=dict(color="#666", size=11),
        showgrid=False,
    ),
    xaxis=dict(showgrid=False, showticklabels=False),
)

st.plotly_chart(fig, use_container_width=True)

# ── Completion bar chart ──────────────────────────────────────────────────────
st.markdown("### 30-Day Completion Rates")

df = pd.DataFrame([{
    "Habit": s["name"],
    "Completion %": s["completion_rate_30d"],
    "Streak": s["current_streak"],
} for s in stats]).sort_values("Completion %", ascending=True)

fig2 = px.bar(
    df,
    x="Completion %",
    y="Habit",
    orientation="h",
    color="Completion %",
    color_continuous_scale=[[0, "#ef4444"], [0.5, "#f59e0b"], [1, "#22c55e"]],
    range_color=[0, 100],
    text="Completion %",
)
fig2.update_traces(texttemplate="%{text}%", textposition="outside")
fig2.update_layout(
    height=max(200, len(stats) * 55),
    margin=dict(l=10, r=60, t=10, b=10),
    paper_bgcolor="rgba(0,0,0,0)",
    plot_bgcolor="rgba(0,0,0,0)",
    coloraxis_showscale=False,
    xaxis=dict(showgrid=False, range=[0, 115], showticklabels=False, color="#666"),
    yaxis=dict(color="#aaa", tickfont=dict(size=13)),
)

st.plotly_chart(fig2, use_container_width=True)
