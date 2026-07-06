import streamlit as st
import uuid
import json
from transcriber import transcribe
from task_extractor import extract_tasks
from rag_engine import store_memo, query_memos

st.set_page_config(page_title="Voice2Tasks", layout="wide")
st.title("🎙️ Voice2Tasks")
st.caption("Upload voice memos → Get structured tasks → Kanban board + RAG chat")

# Initialize session state
if "tasks" not in st.session_state:
    st.session_state.tasks = []

# --- Sidebar: Upload & RAG Chat ---
with st.sidebar:
    st.header("📤 Upload Voice Memo")
    audio_file = st.file_uploader("Upload audio", type=["wav", "mp3", "m4a", "ogg"])

    if audio_file and st.button("🎯 Process Memo"):
        with st.spinner("Transcribing..."):
            transcription = transcribe(audio_file)
            st.success("Transcription done!")
            st.text_area("Transcription", transcription, height=150)

        with st.spinner("Extracting tasks..."):
            tasks = extract_tasks(transcription)

            # Add unique IDs and append to session state
            for task in tasks:
                task["id"] = str(uuid.uuid4())[:8]
                if "status" not in task:
                    task["status"] = "todo"
                st.session_state.tasks.append(task)

            # Store in RAG
            memo_id = str(uuid.uuid4())[:8]
            tasks_text = json.dumps(tasks, indent=2)
            store_memo(memo_id, transcription, tasks_text)

            st.success(f"Extracted {len(tasks)} tasks!")

    st.divider()
    st.header("💬 Ask about your memos")
    question = st.text_input("Ask a question")
    if question and st.button("🔍 Search"):
        with st.spinner("Searching..."):
            answer = query_memos(question)
            st.markdown(answer)

# --- Main Area: Kanban Board ---
st.header("📋 Kanban Board")

col1, col2, col3 = st.columns(3)

todo_tasks = [t for t in st.session_state.tasks if t.get("status") == "todo"]
in_progress_tasks = [t for t in st.session_state.tasks if t.get("status") == "in-progress"]
done_tasks = [t for t in st.session_state.tasks if t.get("status") == "done"]

PRIORITY_COLORS = {"high": "🔴", "medium": "🟡", "low": "🟢"}


def render_task(task, column_key):
    """Render a single task card with status change buttons."""
    priority_icon = PRIORITY_COLORS.get(task.get("priority", "low"), "⚪")
    st.markdown(f"**{priority_icon} {task['title']}**")
    st.caption(task.get("description", ""))
    st.caption(f"Category: {task.get('category', 'general')}")

    # Status change buttons
    new_status = st.selectbox(
        "Move to",
        ["todo", "in-progress", "done"],
        index=["todo", "in-progress", "done"].index(task.get("status", "todo")),
        key=f"{column_key}_{task['id']}",
    )
    if new_status != task.get("status"):
        task["status"] = new_status
        st.rerun()

    st.divider()


with col1:
    st.subheader(f"📝 Todo ({len(todo_tasks)})")
    for task in todo_tasks:
        render_task(task, "todo")

with col2:
    st.subheader(f"🚧 In Progress ({len(in_progress_tasks)})")
    for task in in_progress_tasks:
        render_task(task, "progress")

with col3:
    st.subheader(f"✅ Done ({len(done_tasks)})")
    for task in done_tasks:
        render_task(task, "done")

# --- Export ---
st.divider()
if st.session_state.tasks:
    export_lines = []
    for task in st.session_state.tasks:
        priority_icon = PRIORITY_COLORS.get(task.get("priority", "low"), "")
        status_mark = "x" if task.get("status") == "done" else " "
        export_lines.append(
            f"[{status_mark}] {priority_icon} {task['title']} - {task.get('description', '')} "
            f"(Priority: {task.get('priority', 'low')}, Category: {task.get('category', 'general')})"
        )

    export_text = "VOICE2TASKS - Todo List\n" + "=" * 40 + "\n\n" + "\n".join(export_lines)

    st.download_button(
        label="📥 Download Tasks (.txt)",
        data=export_text,
        file_name="voice2tasks_export.txt",
        mime="text/plain",
    )
