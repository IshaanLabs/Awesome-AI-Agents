from typing import TypedDict

from langgraph.graph import StateGraph, END

from agents import therapist_agent, closure_agent, routine_planner_agent, brutal_honesty_agent


# ── State ─────────────────────────────────────────────────────────────────────
class RecoveryState(TypedDict):
    user_text:       str
    image_paths:     list[str]
    therapist_out:   str
    closure_out:     str
    routine_out:     str
    honesty_out:     str


# ── Graph Nodes ───────────────────────────────────────────────────────────────
def node_therapist(state: RecoveryState) -> RecoveryState:
    print("[main] Graph node: therapist")
    result = therapist_agent(state["user_text"], state["image_paths"])
    return {**state, "therapist_out": result}


def node_closure(state: RecoveryState) -> RecoveryState:
    print("[main] Graph node: closure")
    result = closure_agent(state["user_text"], state["image_paths"])
    return {**state, "closure_out": result}


def node_routine(state: RecoveryState) -> RecoveryState:
    print("[main] Graph node: routine planner")
    result = routine_planner_agent(state["user_text"], state["image_paths"])
    return {**state, "routine_out": result}


def node_honesty(state: RecoveryState) -> RecoveryState:
    print("[main] Graph node: brutal honesty")
    result = brutal_honesty_agent(state["user_text"], state["image_paths"])
    return {**state, "honesty_out": result}


# ── Build Graph ───────────────────────────────────────────────────────────────
def build_graph() -> StateGraph:
    print("[main] Building LangGraph recovery graph")
    graph = StateGraph(RecoveryState)

    graph.add_node("therapist", node_therapist)
    graph.add_node("closure",   node_closure)
    graph.add_node("routine",   node_routine)
    graph.add_node("honesty",   node_honesty)

    graph.set_entry_point("therapist")
    graph.add_edge("therapist", "closure")
    graph.add_edge("closure",   "routine")
    graph.add_edge("routine",   "honesty")
    graph.add_edge("honesty",   END)

    return graph.compile()


# ── Public Runner ─────────────────────────────────────────────────────────────
def run_graph(user_text: str, image_paths: list[str]) -> dict:
    print("[main] Starting recovery graph run")

    initial_state: RecoveryState = {
        "user_text":     user_text,
        "image_paths":   image_paths,
        "therapist_out": "",
        "closure_out":   "",
        "routine_out":   "",
        "honesty_out":   "",
    }

    app    = build_graph()
    result = app.invoke(initial_state)

    print("[main] Recovery graph run completed")
    return result


# ── CLI test ──────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    output = run_graph("We broke up after 3 years. I feel lost and don't know what to do.", [])
    print("\n=== THERAPIST ===\n",  output["therapist_out"])
    print("\n=== CLOSURE ===\n",    output["closure_out"])
    print("\n=== ROUTINE ===\n",    output["routine_out"])
    print("\n=== HONESTY ===\n",    output["honesty_out"])
