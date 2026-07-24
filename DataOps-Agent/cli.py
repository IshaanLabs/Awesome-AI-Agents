import sys
sys.path.insert(0, "/mnt/d/awesome/SQL_AI/DataOps-Agent")
sys.path.append("/mnt/d/awesome/SQL_AI")

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.markdown import Markdown

from config import AGENT_USER_ID, MCP_URL
from agent import run_agent
from memory import get_recent_memory, get_memory
from logger import get_logger

log = get_logger("cli")
console = Console()

COMMANDS = {
    "/tables":  "List all database tables",
    "/memory":  "Show recent memory for current user",
    "/history": "Show recent audit logs",
    "/clear":   "Clear memory for current user",
    "/help":    "Show this help",
    "/quit":    "Exit",
}


def show_help():
    table = Table(title="DataOps Agent Commands", show_header=True)
    table.add_column("Command", style="cyan")
    table.add_column("Description")
    for cmd, desc in COMMANDS.items():
        table.add_row(cmd, desc)
    console.print(table)


def handle_command(cmd: str, user_id: str) -> bool:
    """Returns True if handled as a command."""
    cmd = cmd.strip().lower()

    if cmd == "/quit":
        console.print("[yellow]Goodbye![/yellow]")
        sys.exit(0)

    elif cmd == "/help":
        show_help()

    elif cmd == "/tables":
        result = run_agent("List all database tables", user_id)
        console.print(Markdown(result))

    elif cmd == "/history":
        result = run_agent("Show me the last 10 audit log entries", user_id)
        console.print(Markdown(result))

    elif cmd == "/memory":
        memories = get_recent_memory(user_id, limit=10)
        if memories:
            for i, m in enumerate(memories, 1):
                console.print(f"[dim]{i}.[/dim] {m}")
        else:
            console.print("[dim]No memory found.[/dim]")

    elif cmd == "/clear":
        try:
            get_memory().delete_all(user_id=user_id)
            console.print("[green]Memory cleared.[/green]")
        except Exception as e:
            console.print(f"[red]Failed to clear memory: {e}[/red]")

    else:
        return False

    return True


def main():
    user_id = AGENT_USER_ID

    console.print(Panel(
        "[bold cyan]DataOps Agent[/bold cyan]\n"
        f"[dim]MCP: {MCP_URL} | User: {user_id}[/dim]\n"
        "Type [cyan]/help[/cyan] for commands or ask anything in natural language.",
        title="🤖 DataOps Agent",
        border_style="cyan",
    ))

    while True:
        try:
            user_input = console.input("\n[bold green]You>[/bold green] ").strip()
        except (KeyboardInterrupt, EOFError):
            console.print("\n[yellow]Goodbye![/yellow]")
            break

        if not user_input:
            continue

        if handle_command(user_input, user_id):
            continue

        console.print("[dim]Thinking...[/dim]")
        try:
            response = run_agent(user_input, user_id, get_input=input)
            console.print(Panel(Markdown(response), border_style="green", title="Agent"))
        except Exception as e:
            log.error(f"Agent error: {e}")
            console.print(f"[red]Error: {e}[/red]")


if __name__ == "__main__":
    main()
