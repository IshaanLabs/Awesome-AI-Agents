from typing import Literal

from colorama import Fore, init
from langchain.messages import AIMessage, HumanMessage
from langgraph.graph import END
from langgraph.types import Send

from src.utils.states import GenerateAnalystsState, InterviewState, ResearchGraphState

init(autoreset=True)


def should_continue(state: GenerateAnalystsState) -> Literal["create_analysts", "dummy"]:
    feedback = state.get("human_analyst_feedback", None)

    if feedback:
        if feedback.lower() == "perfect":
            print(Fore.GREEN + "[should_continue] Feedback is 'perfect' — moving to end.")
            return "dummy"
        print(Fore.YELLOW + f"[should_continue] Feedback provided — regenerating analysts.")
        return "create_analysts"

    print(Fore.GREEN + "[should_continue] No feedback — analysts approved.")
    return "dummy"


def route_messages(state: InterviewState, name: str = "expert") -> Literal["ask_question", "save_interview"]:
    messages     = state["messages"]
    max_num_turns = state.get("max_num_turns", 2)

    num_responses = len([m for m in messages if isinstance(m, AIMessage) and m.name == name])
    print(Fore.BLUE + f"[route_messages] Expert responses so far: {num_responses}/{max_num_turns}")

    if num_responses >= max_num_turns:
        print(Fore.YELLOW + "[route_messages] Max turns reached — saving interview.")
        return "save_interview"

    last_question = messages[-2]
    if "Thank you so much for your help" in last_question.content:
        print(Fore.YELLOW + "[route_messages] Analyst closed the interview — saving.")
        return "save_interview"

    print(Fore.BLUE + "[route_messages] Continuing interview — asking next question.")
    return "ask_question"


def initiate_all_interviews(state: ResearchGraphState):
    feedback = state.get("human_analyst_feedback")

    if feedback:
        print(Fore.YELLOW + "[initiate_all_interviews] Feedback present — returning to create_analysts.")
        return "create_analysts"

    topic    = state["topic"]
    analysts = state["analysts"]
    print(Fore.CYAN + f"[initiate_all_interviews] Fanning out {len(analysts)} interview(s) in parallel...")

    return [
        Send("conduct_interview", {
            "analyst": analyst,
            "messages": [HumanMessage(content=f"So you said you were writing an article on {topic}?")]
        })
        for analyst in analysts
    ]
