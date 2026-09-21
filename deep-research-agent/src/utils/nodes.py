from colorama import Fore, Style, init
from dotenv import load_dotenv
from langchain.messages import SystemMessage, HumanMessage
from langchain_core.messages import get_buffer_string
from langchain_tavily import TavilySearch
from langgraph.types import interrupt

import os
from src.utils.config import TAVILY_API_KEY, TAVILY_MAX_RESULTS
os.environ["TAVILY_API_KEY"] = TAVILY_API_KEY
from src.utils.models import llm, llm_json
from src.utils.objects import Analyst, Perspectives
from src.utils.prompts import (
    analyst_instructions,
    answer_instructions,
    intro_conclusion_instructions,
    question_instructions,
    report_writer_instructions,
    search_instructions,
    section_writer_instructions,
)
from src.utils.states import (
    GenerateAnalystsState,
    InterviewState,
    ResearchGraphState,
    SearchQuery,
)

init(autoreset=True)
load_dotenv()

tavily_search = TavilySearch(max_results=TAVILY_MAX_RESULTS)


# ── Analyst generation ─────────────────────────────────────────────────────────

def create_analysts(state: GenerateAnalystsState):
    topic                 = state["topic"]
    max_analysts          = state["max_analysts"]
    human_analyst_feedback = state.get("human_analyst_feedback", "")

    print(Fore.CYAN + f"\n[create_analysts] Generating {max_analysts} analyst(s) for topic: '{topic}'")
    if human_analyst_feedback:
        print(Fore.YELLOW + f"[create_analysts] Applying human feedback: {human_analyst_feedback}")

    structured_llm = llm_json.with_structured_output(Perspectives)
    system_message = analyst_instructions.format(
        topic=topic,
        human_analyst_feedback=human_analyst_feedback,
        max_analysts=max_analysts,
    )
    analysts = structured_llm.invoke(
        [SystemMessage(content=system_message), HumanMessage(content="Generate the set of analysts.")]
    )

    print(Fore.GREEN + f"[create_analysts] Created {len(analysts.analysts)} analyst(s):")
    for a in analysts.analysts:
        print(Fore.GREEN + f"  • {a.name} | {a.role} | {a.affiliation}")

    return {"analysts": analysts.analysts}


def human_feedback(state: GenerateAnalystsState):
    print(Fore.MAGENTA + "\n[human_feedback] Waiting for human approval of analysts...")

    feedback = interrupt({
        "question": "Are these analysts okay?",
        "analysts": [
            a.model_dump() if hasattr(a, "model_dump") else a
            for a in state.get("analysts", [])
        ],
        "instructions": "Return feedback to regenerate analysts, or return empty/perfect/continue to approve.",
    })

    if feedback is None or (isinstance(feedback, str) and feedback.strip() == ""):
        print(Fore.GREEN + "[human_feedback] Approved — no feedback provided.")
        return {"human_analyst_feedback": None}

    if isinstance(feedback, str):
        feedback = feedback.strip()
        if feedback.lower() in {"perfect", "continue", "approved", "yes", ""}:
            print(Fore.GREEN + f"[human_feedback] Approved with keyword: '{feedback}'")
            return {"human_analyst_feedback": None}
        print(Fore.YELLOW + f"[human_feedback] Feedback received: '{feedback}'")
        return {"human_analyst_feedback": feedback}

    return {"human_analyst_feedback": None}


def dummy(state: GenerateAnalystsState):
    print(Fore.CYAN + "[dummy] Analyst review complete. Moving on.")


# ── Interview nodes ────────────────────────────────────────────────────────────

def generate_question(state: InterviewState):
    analyst  = state["analyst"]
    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)
    messages = state["messages"]

    print(Fore.CYAN + f"\n[generate_question] Analyst '{analyst.name}' is forming a question...")

    system_message = question_instructions.format(goals=analyst.persona)
    question = llm.invoke([SystemMessage(content=system_message)] + messages)

    print(Fore.CYAN + f"[generate_question] Question:\n{question.content}")
    return {"messages": [question]}


def _run_search(state: InterviewState, label: str):
    """Shared search logic used by both search nodes."""
    print(Fore.BLUE + f"\n[{label}] Generating search query from conversation...")

    messages      = state["messages"]
    last_question = next(
        (m for m in reversed(messages) if not (hasattr(m, "name") and m.name == "expert")),
        messages[-1] if messages else None,
    )
    focused_messages = [last_question] if last_question else messages

    structured_llm = llm_json.with_structured_output(SearchQuery)
    search_query   = structured_llm.invoke(
        [SystemMessage(content=search_instructions)] + focused_messages
    )

    query = search_query.search_query if search_query and search_query.search_query else None

    if not query:
        print(Fore.YELLOW + f"[{label}] Structured output returned None — falling back to last question...")
        raw   = last_question.content if last_question else ""
        query = [line.strip() for line in raw.strip().splitlines() if line.strip()][-1] if raw else ""

    print(Fore.BLUE + f"[{label}] Search query: '{query}'")

    data        = tavily_search.invoke({"query": query})
    search_docs = data.get("results", data)
    search_docs = [doc for doc in search_docs if isinstance(doc, dict)]

    print(Fore.BLUE + f"[{label}] Retrieved {len(search_docs)} document(s).")

    if not search_docs:
        print(Fore.RED + f"[{label}] No valid documents retrieved — returning empty context.")
        return {"context": []}

    formatted = "\n\n---\n\n".join(
        f'<Document href="{doc["url"]}"/>\n{doc["content"]}\n</Document>'
        for doc in search_docs
    )
    return {"context": [formatted]}


def search_web(state: InterviewState):
    return _run_search(state, "search_web")


def search_web2(state: InterviewState):
    return _run_search(state, "search_web2")


def generate_answer(state: InterviewState):
    analyst  = state["analyst"]
    messages = state["messages"]
    context  = state["context"]

    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)

    print(Fore.YELLOW + f"\n[generate_answer] Expert answering question for analyst '{analyst.name}'...")

    system_message = answer_instructions.format(goals=analyst.persona, context=context)
    answer         = llm.invoke([SystemMessage(content=system_message)] + messages)
    answer.name    = "expert"

    print(Fore.YELLOW + f"[generate_answer] Answer:\n{answer.content}")
    return {"messages": [answer]}


def save_interview(state: InterviewState):
    print(Fore.CYAN + "\n[save_interview] Saving interview transcript...")
    interview = get_buffer_string(state["messages"])
    print(Fore.CYAN + f"[save_interview] Transcript length: {len(interview)} characters.")
    return {"interview": interview, "sections": [], "interviews": [interview]}


def write_section(state: InterviewState):
    interview = state["interview"]
    context   = state["context"]
    analyst   = state["analyst"]

    if isinstance(analyst, dict):
        analyst = Analyst.model_validate(analyst)

    print(Fore.YELLOW + f"\n[write_section] Writing report section for analyst '{analyst.name}'...")

    system_message = section_writer_instructions.format(focus=analyst.description)
    section = llm.invoke(
        [SystemMessage(content=system_message),
         HumanMessage(content=f"Use this source to write your section: {context}")]
    )

    print(Fore.GREEN + f"[write_section] Section written ({len(section.content)} characters).")
    return {"sections": [section.content]}


# ── Report nodes ───────────────────────────────────────────────────────────────

def write_report(state: ResearchGraphState):
    print(Fore.CYAN + "\n[write_report] Consolidating analyst memos into report body...")

    sections              = state["sections"]
    topic                 = state["topic"]
    formatted_str_sections = "\n\n".join(sections)

    system_message = report_writer_instructions.format(topic=topic, context=formatted_str_sections)
    report = llm.invoke(
        [SystemMessage(content=system_message),
         HumanMessage(content="Write a report based upon these memos.")]
    )

    print(Fore.GREEN + f"[write_report] Report body written ({len(report.content)} characters).")
    return {"content": report.content}


def write_introduction(state: ResearchGraphState):
    print(Fore.CYAN + "\n[write_introduction] Writing report introduction...")

    sections              = state["sections"]
    topic                 = state["topic"]
    formatted_str_sections = "\n\n".join(sections)

    instructions = intro_conclusion_instructions.format(
        topic=topic, formatted_str_sections=formatted_str_sections
    )
    intro = llm.invoke([SystemMessage(content=instructions), HumanMessage(content="Write the report introduction")])

    print(Fore.GREEN + "[write_introduction] Introduction written.")
    return {"introduction": intro.content}


def write_conclusion(state: ResearchGraphState):
    print(Fore.CYAN + "\n[write_conclusion] Writing report conclusion...")

    sections              = state["sections"]
    topic                 = state["topic"]
    formatted_str_sections = "\n\n".join(sections)

    instructions = intro_conclusion_instructions.format(
        topic=topic, formatted_str_sections=formatted_str_sections
    )
    conclusion = llm.invoke([SystemMessage(content=instructions), HumanMessage(content="Write the report conclusion")])

    print(Fore.GREEN + "[write_conclusion] Conclusion written.")
    return {"conclusion": conclusion.content}


def finalize_report(state: ResearchGraphState):
    print(Fore.CYAN + "\n[finalize_report] Assembling final report...")

    content = state["content"]
    if content.startswith("## Insights"):
        content = content.strip("## Insights")

    if "## Sources" in content:
        try:
            content, sources = content.split("\n## Sources\n")
        except Exception:
            sources = None
    else:
        sources = None

    final_report = (
        state["introduction"]
        + "\n\n---\n\n"
        + content
        + "\n\n---\n\n"
        + state["conclusion"]
    )
    if sources:
        final_report += "\n\n## Sources\n" + sources

    # build full conversation log from all interview transcripts
    analysts   = state.get("analysts", [])
    interviews = state.get("interviews", [])
    topic      = state["topic"]
    log_parts  = [f"# Full Research Conversation Log\n\n**Topic:** {topic}\n"]
    for i, transcript in enumerate(interviews):
        name = analysts[i].name if i < len(analysts) and hasattr(analysts[i], "name") else f"Analyst {i+1}"
        log_parts.append(f"\n---\n\n## Interview {i+1} — {name}\n\n{transcript}")
    conversation_log = "\n".join(log_parts)

    print(Fore.GREEN + f"[finalize_report] Final report ready ({len(final_report)} characters).")
    return {"final_report": final_report, "conversation_log": conversation_log}
