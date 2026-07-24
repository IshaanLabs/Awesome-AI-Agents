import asyncio
import sys
sys.path.insert(0, "/mnt/d/awesome/SQL_AI/DataOps-Agent")
sys.path.append("/mnt/d/awesome/SQL_AI")

from fastmcp import Client
from langchain_core.tools import tool
from config import MCP_URL
from logger import get_logger

log = get_logger("tools")


def _call(tool_name: str, **kwargs) -> str:
    async def _run():
        async with Client(MCP_URL) as client:
            result = await client.call_tool(tool_name, kwargs)
            return result.content[0].text if result.content else "No result"
    try:
        return asyncio.run(_run())
    except Exception as e:
        log.error(f"MCP tool {tool_name} failed: {e}")
        return f"Error: {e}"


@tool
def ask_database(question: str) -> str:
    """Ask a natural language question about the database. Handles SELECT, INSERT, UPDATE, DELETE with safety checks."""
    log.info(f"ask_database: {question}")
    return _call("ask_database", question=question)


@tool
def get_tables() -> str:
    """List all available database tables."""
    return _call("get_tables")


@tool
def get_database_schema(table_names: str = "") -> str:
    """Get DDL schema for tables. Pass comma-separated table names or empty for all."""
    return _call("get_database_schema", table_names=table_names)


@tool
def describe_database_table(table_name: str) -> str:
    """Get detailed schema information for a specific table."""
    return _call("describe_database_table", table_name=table_name)


@tool
def run_read_query(sql: str) -> str:
    """Execute a raw SELECT query directly against the database."""
    log.info(f"run_read_query: {sql}")
    return _call("run_read_query", sql=sql)


@tool
def explain_sql(sql: str) -> str:
    """Explain what a SQL query does in plain English."""
    return _call("explain_sql", sql=sql)


@tool
def preview_write_operation(sql: str) -> str:
    """Preview the impact of a write operation (dry run) without executing it."""
    log.info(f"preview_write_operation: {sql}")
    return _call("preview_write_operation", sql=sql)


@tool
def approve_operation(thread_id: str, approved_by: str = "dataops_agent") -> str:
    """Approve a pending write operation that requires human approval."""
    log.info(f"approve_operation: thread_id={thread_id}")
    return _call("approve_operation", thread_id=thread_id, approved_by=approved_by)


@tool
def reject_operation(thread_id: str, reason: str = "") -> str:
    """Reject a pending write operation."""
    log.info(f"reject_operation: thread_id={thread_id}")
    return _call("reject_operation", thread_id=thread_id, reason=reason)


@tool
def get_audit_logs(limit: int = 10) -> str:
    """Get recent execution audit logs showing past database operations."""
    return _call("get_audit_logs", limit=limit)


ALL_TOOLS = [
    ask_database,
    get_tables,
    get_database_schema,
    describe_database_table,
    run_read_query,
    explain_sql,
    preview_write_operation,
    approve_operation,
    reject_operation,
    get_audit_logs,
]
