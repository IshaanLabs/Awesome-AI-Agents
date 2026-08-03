import os
import re

from dotenv import load_dotenv
from langchain_core.chat_history import InMemoryChatMessageHistory
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_ollama import ChatOllama

load_dotenv()

SYSTEM_PROMPT = """You turn the user's brief into a short email.

Hard rules:
- Plain office English. Write like a real colleague, not marketing copy.
- Body: 3-5 sentences max unless the user asks for longer.
- Use only facts from the brief. Never invent who did what.
- The recipient must do what the brief says THEY should do. Do not assign their tasks to the sender.
- No emojis. No slang (ya, gonna, stuff). No idioms. No "Cheers" or "Hope this finds you well".
- No sign-off placeholder like [Your Name] — end with "Thanks" or nothing.

"""


def get_llm():
    print("[1] loading ChatOllama from env")
    return ChatOllama(
        base_url=os.environ["OLLAMA_BASE_URL"],
        model=os.environ["OLLAMA_MODEL"],
        temperature=0.1,
    )


def get_prompt():
    print("[2] building ChatPromptTemplate")
    return ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        MessagesPlaceholder("history"),
        ("human", "{input}"),
    ])


def get_chain():
    print("[3] wiring prompt | llm")
    return get_prompt() | get_llm()


def parse_email(text):
    print("[4] parsing subject + body from model output")
    subject_match = re.search(r"SUBJECT:\s*(.+)", text)
    body_match = re.search(r"BODY:\s*\n?(.*)", text, re.DOTALL)
    subject = subject_match.group(1).strip() if subject_match else ""
    body = body_match.group(1).strip() if body_match else text.strip()
    body = re.sub(r"\[Your Name\]\s*", "", body).strip()
    return subject, body


def revision_rules(feedback):
    f = feedback.lower()
    rules = []
    if any(w in f for w in ("concise", "short", "small", "brief", "shorter")):
        rules.append("Body must be 3 sentences or fewer.")
    if any(w in f for w in ("human", "plain", "simple", "general")):
        rules.append("Use normal conversational office English. No hype words (Good stuff, ASAP, smooth).")
    return " ".join(rules)


def build_revision_input(original_brief, feedback, prev_subject, prev_body):
    print("[5a] building revision prompt (fresh context, no chat history)")
    extra = revision_rules(feedback)
    parts = [
        "Rewrite the email below. Keep the same facts as the original brief.",
        "Apply the feedback. Do not add new facts or tasks.",
        extra,
        f"\nOriginal brief:\n{original_brief}",
        f"\nPrevious draft:\nSUBJECT: {prev_subject}\nBODY:\n{prev_body}",
        f"\nFeedback:\n{feedback}",
    ]
    return "\n".join(p for p in parts if p)


def generate_email(user_input, history, original_brief=None, prev_subject=None, prev_body=None):
    is_revision = original_brief and prev_subject is not None
    print(f"[5] generate_email called, revision={is_revision}, history={len(history.messages)} msgs")

    if is_revision:
        user_input = build_revision_input(original_brief, user_input, prev_subject, prev_body)
        chat_history = []  # ponytail: bad first draft was poisoning follow-ups
    else:
        chat_history = history.messages

    chain = get_chain()
    response = chain.invoke({"input": user_input, "history": chat_history})
    text = response.content
    print("[6] got model response, updating history")
    history.add_user_message(user_input)
    history.add_ai_message(text)
    subject, body = parse_email(text)
    print(f"[7] done — subject={subject[:50]!r}...")
    return subject, body


def new_history():
    print("[0] new InMemoryChatMessageHistory")
    return InMemoryChatMessageHistory()


if __name__ == "__main__":
    sample = "SUBJECT: Hello\nBODY:\nDear team,\n\nThanks.\n"
    s, b = parse_email(sample)
    assert s == "Hello" and "Dear team" in b

    sample2 = "SUBJECT: Hi\nBODY:\nThanks.\n\nCheers, [Your Name]"
    s2, b2 = parse_email(sample2)
    assert "[Your Name]" not in b2
