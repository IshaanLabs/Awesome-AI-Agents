from langchain_ollama import OllamaLLM
from datetime import datetime
import os

MODEL_NAME = "qwen2.5:7b-instruct-q4_K_M"
BASE_URL = "http://localhost:11434"
OUTPUT_DIR = "output"


def get_llm():
    return OllamaLLM(model=MODEL_NAME, base_url=BASE_URL, temperature=0.2)


# ── Step 1: Clean transcript ──────────────────────────────────────────────────
def clean_transcript(llm, transcript):
    print("[STEP 1] Cleaning transcript — removing noise, filler words, incomplete sentences")
    prompt = f"""You are a transcript editor. Clean the following raw meeting transcript by:
- Removing filler words (uh, mm, yeah, okay used as filler, etc.)
- Removing incomplete or incoherent sentences
- Removing transcription noise (single words with no context)
- Keeping all meaningful dialogue and attributing it to the correct speaker
- Preserving speaker names and the flow of conversation

Output ONLY the cleaned transcript. No commentary.

RAW TRANSCRIPT:
{transcript}

CLEANED TRANSCRIPT:"""
    result = llm.invoke(prompt)
    print(f"[STEP 1] Done. Cleaned transcript length: {len(result)} chars")
    return result


# ── Step 2: Extract metadata ──────────────────────────────────────────────────
def extract_metadata(llm, cleaned_transcript):
    print("[STEP 2] Extracting metadata — attendees, date, meeting type")
    prompt = f"""From the meeting transcript below, extract the following in JSON format:
- "date": meeting date (if not mentioned, use "Not Specified")
- "attendees": list of all attendee full names found in the transcript
- "meeting_type": infer the type of meeting (e.g. Technical Design Discussion, Planning, Review, etc.)
- "title": a short descriptive title for this meeting based on the topics discussed

Output ONLY valid JSON. No commentary.

TRANSCRIPT:
{cleaned_transcript}

JSON:"""
    result = llm.invoke(prompt)
    print(f"[STEP 2] Done. Metadata: {result[:200]}")
    return result


# ── Step 3: Extract key topics ────────────────────────────────────────────────
def extract_topics(llm, cleaned_transcript):
    print("[STEP 3] Extracting key discussion topics from transcript")
    prompt = f"""Read the meeting transcript below and identify ALL distinct topics that were discussed.
For each topic:
- Give it a clear professional name
- Write 3 to 5 sentences summarizing what was discussed about that topic
- List any specific requirements, decisions, or technical details mentioned

Format as markdown with ### headings for each topic. Be thorough and detailed.
Output ONLY the topics section. No commentary.

TRANSCRIPT:
{cleaned_transcript}

KEY TOPICS:"""
    result = llm.invoke(prompt)
    print(f"[STEP 3] Done. Topics length: {len(result)} chars")
    return result


# ── Step 4: Executive summary ─────────────────────────────────────────────────
def generate_executive_summary(llm, cleaned_transcript, topics):
    print("[STEP 4] Generating executive summary")
    prompt = f"""Based on the meeting transcript and key topics below, write an Executive Summary of the meeting.
The summary must be 5 to 7 bullet points, each a complete professional sentence.
Cover the most important outcomes, decisions, and goals of the meeting.
Output ONLY the bullet points. No heading, no commentary.

TRANSCRIPT:
{cleaned_transcript}

KEY TOPICS:
{topics}

EXECUTIVE SUMMARY BULLET POINTS:"""
    result = llm.invoke(prompt)
    print(f"[STEP 4] Done. Summary length: {len(result)} chars")
    return result


# ── Step 5: Decisions made ────────────────────────────────────────────────────
def extract_decisions(llm, cleaned_transcript, topics):
    print("[STEP 5] Extracting decisions made during the meeting")
    prompt = f"""From the meeting transcript and topics below, extract ALL decisions that were made or agreed upon.
Write each decision as a clear, complete sentence starting with an action verb.
Number each decision. Be specific — avoid vague statements.
Output ONLY the numbered list of decisions. No commentary.

TRANSCRIPT:
{cleaned_transcript}

KEY TOPICS:
{topics}

DECISIONS MADE:"""
    result = llm.invoke(prompt)
    print(f"[STEP 5] Done. Decisions length: {len(result)} chars")
    return result


# ── Step 6: Action items ──────────────────────────────────────────────────────
def extract_action_items(llm, cleaned_transcript, decisions):
    print("[STEP 6] Extracting action items")
    prompt = f"""From the meeting transcript and decisions below, create a detailed Action Items table.
Each row must have: Owner, Task, Due Date (use "Not Specified" if not mentioned), Status (Open/In Progress).
Every attendee mentioned in the transcript must have at least one action item.
Tasks must be specific and actionable, not vague.
Output ONLY a markdown table with columns: | Owner | Task | Due Date | Status |
No commentary.

TRANSCRIPT:
{cleaned_transcript}

DECISIONS:
{decisions}

ACTION ITEMS TABLE:"""
    result = llm.invoke(prompt)
    print(f"[STEP 6] Done. Action items length: {len(result)} chars")
    return result


# ── Step 7: Risks and open questions ─────────────────────────────────────────
def extract_risks_and_questions(llm, cleaned_transcript, topics):
    print("[STEP 7] Identifying risks and open questions")
    prompt = f"""From the meeting transcript and topics below, identify:

1. OPEN QUESTIONS: Things that were raised but not resolved. List as bullet points.
2. RISKS: At least 4 specific risks related to the project discussed. For each risk:
   - Give it a descriptive name as a ### heading
   - Write 2 to 3 sentences explaining the risk and its potential impact

Output in markdown. Start with "### Open Questions" then "### Risks". No extra commentary.

TRANSCRIPT:
{cleaned_transcript}

KEY TOPICS:
{topics}

RISKS AND OPEN QUESTIONS:"""
    result = llm.invoke(prompt)
    print(f"[STEP 7] Done. Risks length: {len(result)} chars")
    return result


# ── Step 8: Requirements and assumptions ─────────────────────────────────────
def extract_requirements(llm, cleaned_transcript, topics):
    print("[STEP 8] Extracting technical requirements and assumptions")
    prompt = f"""From the meeting transcript and topics below, extract:

1. FUNCTIONAL REQUIREMENTS: What the system must do. Bullet list.
2. NON-FUNCTIONAL REQUIREMENTS: Performance, security, usability, etc. Bullet list.
3. ASSUMPTIONS: What the team is assuming to be true. Bullet list.

Be specific and detailed. Each point must be a complete sentence.
Output in markdown with bold headings for each section. No extra commentary.

TRANSCRIPT:
{cleaned_transcript}

KEY TOPICS:
{topics}

REQUIREMENTS AND ASSUMPTIONS:"""
    result = llm.invoke(prompt)
    print(f"[STEP 8] Done. Requirements length: {len(result)} chars")
    return result


# ── Step 9: Next steps ────────────────────────────────────────────────────────
def generate_next_steps(llm, decisions, action_items):
    print("[STEP 9] Generating next steps")
    prompt = f"""Based on the decisions and action items below, write a numbered list of concrete Next Steps for the team.
Each step must be specific, actionable, and tied to the project goals.
Write at least 6 next steps. Each must be a complete sentence.
Output ONLY the numbered list. No commentary.

DECISIONS:
{decisions}

ACTION ITEMS:
{action_items}

NEXT STEPS:"""
    result = llm.invoke(prompt)
    print(f"[STEP 9] Done. Next steps length: {len(result)} chars")
    return result


# ── Step 10: Assemble final MOM ───────────────────────────────────────────────
def assemble_mom(metadata, executive_summary, topics, decisions, action_items, risks, requirements, next_steps):
    print("[STEP 10] Assembling final MOM document")

    mom = f"""# Minutes of Meeting

## Meeting Details
{metadata}

---

## Executive Summary
{executive_summary}

---

## Key Discussions
{topics}

---

## Decisions Made
{decisions}

---

## Action Items
{action_items}

---

## Open Questions / Risks / Blockers
{risks}

---

## Technical Requirements & Assumptions
{requirements}

---

## Next Steps
{next_steps}
"""
    print(f"[STEP 10] Final MOM assembled. Total length: {len(mom)} chars")
    return mom


# ── Main orchestrator ─────────────────────────────────────────────────────────
def generate_mom(transcript):
    print("[INFO] Starting MOM generation pipeline")
    llm = get_llm()

    cleaned        = clean_transcript(llm, transcript)
    metadata       = extract_metadata(llm, cleaned)
    topics         = extract_topics(llm, cleaned)
    summary        = generate_executive_summary(llm, cleaned, topics)
    decisions      = extract_decisions(llm, cleaned, topics)
    action_items   = extract_action_items(llm, cleaned, decisions)
    risks          = extract_risks_and_questions(llm, cleaned, topics)
    requirements   = extract_requirements(llm, cleaned, topics)
    next_steps     = generate_next_steps(llm, decisions, action_items)

    mom = assemble_mom(metadata, summary, topics, decisions, action_items, risks, requirements, next_steps)
    print("[INFO] MOM generation pipeline complete")
    return mom


def save_mom_to_file(mom_content):
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"MOM_{timestamp}.md"
    filepath = os.path.join(OUTPUT_DIR, filename)

    print(f"[INFO] Saving MOM to file: {filepath}")
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(mom_content)

    print(f"[INFO] File saved successfully: {filepath}")
    return filepath
