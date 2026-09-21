import uuid
import streamlit as st
from langgraph.types import Command
from src.deep_agent import graph
from src.utils.config import DEFAULT_MAX_ANALYSTS, DEFAULT_MAX_TURNS

# ── Page config ────────────────────────────────────────────────────────────────
st.set_page_config(page_title="ResearchForge", page_icon="🔬", layout="wide")
st.title("🔬 ResearchForge")
st.caption("Multi-agent research assistant powered by Ollama (qwen2.5:14b) + Tavily")

# ── Session state init ─────────────────────────────────────────────────────────
if "phase" not in st.session_state:
    st.session_state.phase            = "input"
    st.session_state.thread_id        = str(uuid.uuid4())
    st.session_state.analysts         = []
    st.session_state.final_report     = ""
    st.session_state.conversation_log = ""

# ── Sidebar config ─────────────────────────────────────────────────────────────
with st.sidebar:
    st.header("⚙️ Configuration")
    max_analysts = st.number_input("Max Analysts", min_value=1, max_value=6, value=DEFAULT_MAX_ANALYSTS)
    max_turns    = st.number_input("Max Interview Turns", min_value=1, max_value=5, value=DEFAULT_MAX_TURNS)
    st.divider()
    st.markdown("**Model:** `qwen2.5:14b` via Ollama")
    st.markdown("**Search:** Tavily")
    if st.button("🔄 Start Over"):
        for key in ["phase", "thread_id", "analysts", "final_report"]:
            del st.session_state[key]
        st.rerun()

thread_config = {"configurable": {"thread_id": st.session_state.thread_id}}

# ── Phase: input ───────────────────────────────────────────────────────────────
if st.session_state.phase == "input":
    st.subheader("Step 1 — Enter your research topic")
    topic = st.text_input("Research Topic", placeholder="e.g. The business impact of RAG in enterprise support teams")

    if st.button("Generate Analysts", disabled=not topic.strip()):
        with st.spinner("Generating analyst personas..."):
            # Run graph until the human_feedback interrupt
            for event in graph.stream(
                {"topic": topic.strip(), "max_analysts": max_analysts, "max_num_turns": max_turns},
                config=thread_config,
                stream_mode="values",
            ):
                if "analysts" in event and event["analysts"]:
                    st.session_state.analysts = event["analysts"]

        st.session_state.phase = "review"
        st.rerun()

# ── Phase: review analysts ─────────────────────────────────────────────────────
elif st.session_state.phase == "review":
    st.subheader("Step 2 — Review Analyst Personas")
    st.info("Review the generated analysts below. Approve them or provide feedback to regenerate.")

    analysts = st.session_state.analysts
    cols = st.columns(len(analysts) if analysts else 1)
    for i, analyst in enumerate(analysts):
        a = analyst if isinstance(analyst, dict) else analyst.model_dump()
        with cols[i]:
            with st.expander(f"**{a['name']}**", expanded=True):
                st.markdown(f"**Role:** {a['role']}")
                st.markdown(f"**Affiliation:** {a['affiliation']}")
                st.markdown(f"**Focus:** {a['description']}")

    st.divider()
    feedback = st.text_area(
        "Feedback (optional)",
        placeholder="Leave blank or type 'approved' to continue, or describe changes you want...",
    )

    col1, col2 = st.columns(2)
    with col1:
        if st.button("✅ Approve & Start Research"):
            with st.spinner("Resuming graph..."):
                for event in graph.stream(
                    Command(resume="approved"),
                    config=thread_config,
                    stream_mode="values",
                ):
                    if "analysts" in event and event["analysts"]:
                        st.session_state.analysts = event["analysts"]

            st.session_state.phase = "researching"
            st.rerun()

    with col2:
        if st.button("🔁 Regenerate with Feedback", disabled=not feedback.strip()):
            with st.spinner("Regenerating analysts..."):
                for event in graph.stream(
                    Command(resume=feedback.strip()),
                    config=thread_config,
                    stream_mode="values",
                ):
                    if "analysts" in event and event["analysts"]:
                        st.session_state.analysts = event["analysts"]

            st.rerun()

# ── Phase: researching ─────────────────────────────────────────────────────────
elif st.session_state.phase == "researching":
    st.subheader("Step 3 — Research in Progress")

    progress_placeholder = st.empty()
    status_log           = []

    with st.status("Running research pipeline...", expanded=True) as status:
        for event in graph.stream(
            Command(resume="approved"),
            config=thread_config,
            stream_mode="values",
        ):
            # Show which nodes have produced output
            for key in ["sections", "content", "introduction", "conclusion", "final_report"]:
                if key in event and event[key]:
                    msg = f"✅ `{key}` ready"
                    if msg not in status_log:
                        status_log.append(msg)
                        st.write(msg)

            if "final_report" in event and event["final_report"]:
                st.session_state.final_report     = event["final_report"]
                st.session_state.conversation_log = event.get("conversation_log", "")
                st.session_state.phase            = "done"
                status.update(label="Research complete!", state="complete")
                st.rerun()

# ── Phase: done ────────────────────────────────────────────────────────────────
elif st.session_state.phase == "done":
    st.subheader("Step 4 — Final Report")
    st.success("Research complete!")

    col1, col2 = st.columns(2)
    with col1:
        st.download_button(
            label="⬇️ Download Report (Markdown)",
            data=st.session_state.final_report,
            file_name="research_report.md",
            mime="text/markdown",
        )
    with col2:
        if st.session_state.conversation_log:
            st.download_button(
                label="💬 Download Full Conversation Log",
                data=st.session_state.conversation_log,
                file_name="conversation_log.md",
                mime="text/markdown",
            )

    st.divider()
    st.markdown(st.session_state.final_report)
