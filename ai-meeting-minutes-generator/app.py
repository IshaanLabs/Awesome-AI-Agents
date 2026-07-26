import streamlit as st
from mom_generator import generate_mom, save_mom_to_file

st.set_page_config(page_title="AI Meeting Minutes Generator", page_icon="📝", layout="wide")

st.title("📝 AI Meeting Minutes Generator")
st.markdown("Paste your meeting transcript below and generate a professional Minutes of Meeting (MOM) document powered by AI.")

transcript = st.text_area(
    label="Meeting Transcript",
    placeholder="Paste your raw meeting transcript here...",
    height=400
)

if st.button("Generate MOM", type="primary"):
    if not transcript.strip():
        st.warning("Please paste a transcript before generating.")
    else:
        print("[INFO] Generate MOM button clicked")

        steps = [
            "Cleaning transcript...",
            "Extracting metadata...",
            "Extracting key topics...",
            "Generating executive summary...",
            "Extracting decisions...",
            "Extracting action items...",
            "Identifying risks & open questions...",
            "Extracting requirements & assumptions...",
            "Generating next steps...",
            "Assembling final MOM...",
        ]

        progress_bar = st.progress(0)
        status_text = st.empty()

        def update_progress(step_index):
            progress = int((step_index / len(steps)) * 100)
            progress_bar.progress(progress)
            status_text.markdown(f"⚙️ **{steps[step_index - 1]}**")
            print(f"[UI] Progress: {progress}% — {steps[step_index - 1]}")

        # Monkey-patch progress updates into the pipeline
        import mom_generator as mg

        original_clean       = mg.clean_transcript
        original_metadata    = mg.extract_metadata
        original_topics      = mg.extract_topics
        original_summary     = mg.generate_executive_summary
        original_decisions   = mg.extract_decisions
        original_actions     = mg.extract_action_items
        original_risks       = mg.extract_risks_and_questions
        original_reqs        = mg.extract_requirements
        original_next        = mg.generate_next_steps
        original_assemble    = mg.assemble_mom

        def wrapped_clean(llm, t):
            update_progress(1)
            return original_clean(llm, t)

        def wrapped_metadata(llm, t):
            update_progress(2)
            return original_metadata(llm, t)

        def wrapped_topics(llm, t):
            update_progress(3)
            return original_topics(llm, t)

        def wrapped_summary(llm, t, topics):
            update_progress(4)
            return original_summary(llm, t, topics)

        def wrapped_decisions(llm, t, topics):
            update_progress(5)
            return original_decisions(llm, t, topics)

        def wrapped_actions(llm, t, decisions):
            update_progress(6)
            return original_actions(llm, t, decisions)

        def wrapped_risks(llm, t, topics):
            update_progress(7)
            return original_risks(llm, t, topics)

        def wrapped_reqs(llm, t, topics):
            update_progress(8)
            return original_reqs(llm, t, topics)

        def wrapped_next(llm, d, a):
            update_progress(9)
            return original_next(llm, d, a)

        def wrapped_assemble(*args, **kwargs):
            update_progress(10)
            return original_assemble(*args, **kwargs)

        mg.clean_transcript             = wrapped_clean
        mg.extract_metadata             = wrapped_metadata
        mg.extract_topics               = wrapped_topics
        mg.generate_executive_summary   = wrapped_summary
        mg.extract_decisions            = wrapped_decisions
        mg.extract_action_items         = wrapped_actions
        mg.extract_risks_and_questions  = wrapped_risks
        mg.extract_requirements         = wrapped_reqs
        mg.generate_next_steps          = wrapped_next
        mg.assemble_mom                 = wrapped_assemble

        mom = generate_mom(transcript)
        filepath = save_mom_to_file(mom)

        # Restore originals
        mg.clean_transcript             = original_clean
        mg.extract_metadata             = original_metadata
        mg.extract_topics               = original_topics
        mg.generate_executive_summary   = original_summary
        mg.extract_decisions            = original_decisions
        mg.extract_action_items         = original_actions
        mg.extract_risks_and_questions  = original_risks
        mg.extract_requirements         = original_reqs
        mg.generate_next_steps          = original_next
        mg.assemble_mom                 = original_assemble

        progress_bar.progress(100)
        status_text.markdown("✅ Done!")

        st.success(f"✅ MOM generated and saved to `{filepath}`")

        col1, col2 = st.columns(2)

        with col1:
            st.subheader("Preview")
            st.markdown(mom)

        with col2:
            st.subheader("Raw Markdown")
            st.text_area(label="", value=mom, height=800)

        st.download_button(
            label="⬇️ Download MOM as .md",
            data=mom,
            file_name=filepath.split("/")[-1],
            mime="text/markdown"
        )
