import argparse
import uuid
from langgraph.types import Command
from src.deep_agent import graph
from src.utils.config import DEFAULT_MAX_ANALYSTS, DEFAULT_MAX_TURNS


def main():
    parser = argparse.ArgumentParser(description="LangGraph Research Assistant CLI")
    parser.add_argument("topic", type=str, help="Research topic")
    parser.add_argument("--analysts", type=int, default=DEFAULT_MAX_ANALYSTS, help="Number of analysts")
    parser.add_argument("--turns", type=int, default=DEFAULT_MAX_TURNS, help="Max interview turns per analyst")
    args = parser.parse_args()

    thread_config = {"configurable": {"thread_id": str(uuid.uuid4())}}

    print(f"\n🔬 ResearchForge")
    print(f"   Topic: '{args.topic}'")
    print(f"   Analysts: {args.analysts} | Max turns: {args.turns}\n")

    # ── Step 1: run until human_feedback interrupt ─────────────────────────────
    for event in graph.stream(
        {"topic": args.topic, "max_analysts": args.analysts, "max_num_turns": args.turns},
        config=thread_config,
        stream_mode="values",
    ):
        if "analysts" in event and event["analysts"]:
            analysts = event["analysts"]

    # ── Step 2: show analysts and ask for approval ─────────────────────────────
    print("\n" + "=" * 60)
    print("GENERATED ANALYSTS")
    print("=" * 60)
    for a in analysts:
        d = a if isinstance(a, dict) else a.model_dump()
        print(f"\n  Name       : {d['name']}")
        print(f"  Role       : {d['role']}")
        print(f"  Affiliation: {d['affiliation']}")
        print(f"  Focus      : {d['description']}")

    print("\n" + "-" * 60)
    feedback = input("Approve analysts? Press Enter to approve or type feedback to regenerate: ").strip()

    # ── Step 3: resume with feedback or approval ───────────────────────────────
    resume_value = "approved" if feedback == "" or feedback.lower() in {"yes", "approved", "perfect", "continue"} else feedback

    result = None
    for event in graph.stream(
        Command(resume=resume_value),
        config=thread_config,
        stream_mode="values",
    ):
        if "final_report" in event and event["final_report"]:
            result = event["final_report"]

    # ── Step 4: print final report ─────────────────────────────────────────────
    print("\n" + "=" * 60)
    print("FINAL REPORT")
    print("=" * 60)
    print(result if result else "No report generated.")


if __name__ == "__main__":
    main()
