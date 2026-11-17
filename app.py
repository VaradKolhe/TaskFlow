"""TaskFlow Streamlit task management dashboard."""

from datetime import date
import sqlite3

import pandas as pd
import plotly.express as px
import streamlit as st

from database import PRIORITIES, STATUSES, create_task, delete_task, get_task, get_tasks, init_db, update_task, update_task_status
from task_logic import completion_stats, validate_task_input

st.set_page_config(page_title="TaskFlow", page_icon="✅", layout="wide")
try:
    init_db()
except sqlite3.Error as exc:
    st.error(f"TaskFlow could not initialize its local database: {exc}")
    st.stop()

st.markdown("""<style>
    .block-container {padding-top: 2rem; padding-bottom: 2rem; max-width: 1440px;}
    [data-testid="stMetric"] {
        background: #2563eb; border: 0; padding: 1rem 1.1rem; border-radius: 14px;
        box-shadow: 0 5px 14px rgba(15, 23, 42, .12); min-height: 112px;
    }
    [data-testid="stMetric"] [data-testid="stMetricLabel"],
    [data-testid="stMetric"] [data-testid="stMetricValue"],
    [data-testid="stMetric"] [data-testid="stMetricDelta"] {color: #fff !important;}
    [data-testid="stMetric"] [data-testid="stMetricLabel"] p {color: #eaf1ff !important; font-weight: 600;}
    [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(2) [data-testid="stMetric"] {background: #d97706;}
    [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(3) [data-testid="stMetric"] {background: #7c3aed;}
    [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(4) [data-testid="stMetric"] {background: #15803d;}
    [data-testid="stHorizontalBlock"] [data-testid="column"]:nth-child(5) [data-testid="stMetric"] {background: #0f766e;}
    h1, h2, h3 {letter-spacing: -0.03em;}
    [data-testid="stCaptionContainer"] {color: #64748b;}
</style>""", unsafe_allow_html=True)

with st.sidebar:
    st.title("✅ TaskFlow")
    st.caption("A clear view of what needs doing.")
    page = st.radio("Navigation", ["Dashboard", "Tasks", "Analytics"], label_visibility="collapsed")
    st.divider()
    st.caption("Tasks are stored locally in SQLite.")

try:
    tasks = get_tasks()
except sqlite3.Error as exc:
    st.error(f"TaskFlow could not read its local database: {exc}")
    st.stop()
stats = completion_stats(tasks)
frame = pd.DataFrame(tasks)

if page == "Dashboard":
    st.title("Dashboard")
    st.caption(f"Your workload at a glance · {date.today().strftime('%A, %B %d, %Y')}")
    cols = st.columns(5)
    cols[0].metric("Total tasks", stats["total"])
    cols[1].metric("Pending", stats["pending"])
    cols[2].metric("In progress", stats["in_progress"])
    cols[3].metric("Completed", stats["completed"])
    cols[4].metric("Completion", f"{stats['completion_pct']}%")
    left, right = st.columns([1, 1.5])
    with left:
        st.subheader("Status distribution")
        counts = pd.DataFrame({"Status": list(STATUSES), "Tasks": [sum(t["status"] == s for t in tasks) for s in STATUSES]})
        fig = px.pie(counts, values="Tasks", names="Status",
                     color="Status", color_discrete_map={"Pending": "#3b82f6", "In Progress": "#f59e0b", "Completed": "#16a34a"},
                     hole=.58)
        fig.update_traces(textinfo="label+percent", textposition="outside", textfont=dict(color="#1e293b", size=13),
                          marker=dict(line=dict(color="#ffffff", width=3)))
        fig.update_layout(
            template="plotly_white", paper_bgcolor="rgba(0,0,0,0)", plot_bgcolor="rgba(0,0,0,0)",
            font=dict(color="#1e293b", size=13), margin=dict(t=20, b=20, l=15, r=15),
            legend_title_text="", legend=dict(font=dict(color="#1e293b", size=13)),
        )
        st.plotly_chart(fig, use_container_width=True)
    with right:
        st.subheader("Recent tasks")
        if not tasks:
            st.info("No tasks yet. Head to **Tasks** to create your first one.")
        else:
            recent = pd.DataFrame(tasks[:5])[ ["title", "priority", "due_date", "status"] ]
            recent.columns = ["Task", "Priority", "Due date", "Status"]
            st.dataframe(recent, use_container_width=True, hide_index=True)

elif page == "Tasks":
    st.title("Tasks")
    st.caption("Create, review, and update your work.")
    with st.expander("＋ Create a task", expanded=not bool(tasks)):
        with st.form("create_task_form", clear_on_submit=True):
            title = st.text_input("Title *", max_chars=120, placeholder="e.g. Prepare project presentation")
            description = st.text_area("Description", max_chars=1000)
            c1, c2, c3 = st.columns(3)
            priority = c1.selectbox("Priority", PRIORITIES, index=1)
            due_date = c2.date_input("Due date", value=None)
            status = c3.selectbox("Status", STATUSES)
            submitted = st.form_submit_button("Create task", type="primary")
        if submitted:
            errors = validate_task_input(title, priority, status, due_date)
            if errors:
                for error in errors: st.error(error)
            else:
                try:
                    create_task(title, description, priority, due_date, status)
                    st.success("Task created.")
                    st.rerun()
                except (ValueError, OSError, sqlite3.Error) as exc:
                    st.error(f"Could not create task: {exc}")

    if tasks:
        f1, f2, f3 = st.columns([2, 1, 1])
        search = f1.text_input("Search", placeholder="Search title or description")
        status_filter = f2.selectbox("Status", ["All statuses", *STATUSES])
        priority_filter = f3.selectbox("Priority", ["All priorities", *PRIORITIES])
        filtered = [t for t in tasks if (not search or search.casefold() in (t["title"] + " " + t["description"]).casefold())
                    and (status_filter == "All statuses" or t["status"] == status_filter)
                    and (priority_filter == "All priorities" or t["priority"] == priority_filter)]
        st.caption(f"Showing {len(filtered)} of {len(tasks)} tasks")
        if filtered:
            table = pd.DataFrame(filtered)[["id", "title", "description", "priority", "due_date", "status"]]
            table.columns = ["ID", "Task", "Description", "Priority", "Due date", "Status"]
            st.dataframe(table, use_container_width=True, hide_index=True)
            st.subheader("Manage a task")
            selected = st.selectbox("Choose task", filtered, format_func=lambda t: f"#{t['id']} · {t['title']}", key="manage_task")
            action_cols = st.columns([1, 2])
            new_status = action_cols[0].selectbox("Update status", STATUSES, index=STATUSES.index(selected["status"]), key=f"status_{selected['id']}")
            if action_cols[0].button("Save status", key=f"save_status_{selected['id']}"):
                try:
                    update_task_status(selected["id"], new_status)
                    st.success("Status updated.")
                    st.rerun()
                except (ValueError, sqlite3.Error) as exc:
                    st.error(f"Could not update status: {exc}")
            with action_cols[1].expander("Edit task"):
                with st.form(f"edit_{selected['id']}"):
                    edit_title = st.text_input("Title", selected["title"], max_chars=120)
                    edit_description = st.text_area("Description", selected["description"])
                    e1, e2, e3 = st.columns(3)
                    edit_priority = e1.selectbox("Priority", PRIORITIES, index=PRIORITIES.index(selected["priority"]))
                    current_due = date.fromisoformat(selected["due_date"]) if selected["due_date"] else None
                    edit_due = e2.date_input("Due date", value=current_due)
                    edit_status = e3.selectbox("Status", STATUSES, index=STATUSES.index(selected["status"]))
                    save_edit = st.form_submit_button("Save changes", type="primary")
                if save_edit:
                    errors = validate_task_input(edit_title, edit_priority, edit_status, edit_due)
                    if errors:
                        for error in errors: st.error(error)
                    else:
                        try:
                            update_task(selected["id"], edit_title, edit_description, edit_priority, edit_due, edit_status)
                            st.success("Task updated.")
                            st.rerun()
                        except (ValueError, sqlite3.Error) as exc:
                            st.error(f"Could not update task: {exc}")
            with st.expander("Delete task"):
                st.warning(f"Delete **{selected['title']}**? This cannot be undone.")
                confirm = st.checkbox("I understand; delete this task", key=f"confirm_delete_{selected['id']}")
                if st.button("Delete task", disabled=not confirm, key=f"delete_{selected['id']}"):
                    try:
                        delete_task(selected["id"])
                        st.success("Task deleted.")
                        st.rerun()
                    except sqlite3.Error as exc:
                        st.error(f"Could not delete task: {exc}")
        else:
            st.info("No tasks match these filters.")
    else:
        st.info("Your task list is empty. Create a task above to get started.")

else:
    st.title("Analytics")
    st.caption("Understand your workload and progress.")
    left, right = st.columns(2)
    with left:
        st.subheader("Tasks by status")
        status_data = pd.DataFrame({"Status": list(STATUSES), "Tasks": [sum(t["status"] == s for t in tasks) for s in STATUSES]})
        st.plotly_chart(px.bar(status_data, x="Status", y="Tasks", color="Status", color_discrete_map={"Pending": "#94a3b8", "In Progress": "#f59e0b", "Completed": "#22c55e"}), use_container_width=True)
    with right:
        st.subheader("Tasks by priority")
        priority_data = pd.DataFrame({"Priority": list(PRIORITIES), "Tasks": [sum(t["priority"] == p for t in tasks) for p in PRIORITIES]})
        st.plotly_chart(px.bar(priority_data, x="Priority", y="Tasks", color="Priority", color_discrete_map={"Low": "#60a5fa", "Medium": "#f59e0b", "High": "#ef4444"}), use_container_width=True)
    st.subheader("Completion statistics")
    st.progress(stats["completion_pct"] / 100, text=f"{stats['completed']} of {stats['total']} tasks completed ({stats['completion_pct']}%)")
    if not tasks: st.info("Analytics will appear here once you add tasks.")
