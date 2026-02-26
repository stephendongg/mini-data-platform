"""Tool functions that the LLM can call via OpenAI function calling.
Each function maps to a tool defined in llm.py."""

from cli.db import run_query

SCHEMA = "marts"


def list_tables(conn):
    """Return all tables in the marts schema with row counts."""
    tables = run_query(conn, f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA}'
        ORDER BY table_name
    """)

    return [
        {
            "table": f"{SCHEMA}.{t['table_name']}",
            "rows": run_query(conn, f"SELECT COUNT(*) as n FROM {SCHEMA}.{t['table_name']}")[0]["n"],
        }
        for t in tables
    ]


def describe_table(conn, table_name):
    """Return columns and types for a specific table."""
    schema, table = table_name.split(".") if "." in table_name else (SCHEMA, table_name)

    return run_query(conn, f"""
        SELECT column_name, data_type
        FROM information_schema.columns
        WHERE table_schema = '{schema}' AND table_name = '{table}'
        ORDER BY ordinal_position
    """)


def run_sql(conn, query):
    """Execute a read-only SQL query and return results."""
    return run_query(conn, query)
