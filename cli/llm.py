"""OpenAI function calling setup.
Defines the tools the LLM can use and the system prompt that guides its behavior."""

import os
from datetime import date
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))
MODEL = "gpt-4o-mini"

SYSTEM_PROMPT = f"""You are an expert data analyst with access to a DuckDB data warehouse.
Use the provided tools to explore the database and answer the user's question.

Workflow:
1. Call list_tables to see what's available
2. Call describe_table on relevant tables to understand their columns
3. Call sample_data to see example values when needed
4. Call run_sql to query the data
5. Provide a clear, concise answer with specific numbers

Rules:
- Always qualify table names with the schema (e.g. marts.fct_orders)
- Use DuckDB SQL syntax
- Only write SELECT queries
- Today's date is {date.today().isoformat()}
- If the data doesn't contain what's needed, say so clearly and explain what's missing. Do not use proxy columns without stating the assumption.
- Plain text only — no markdown, no bold, no headers, no tables"""

# Tool definitions in the format OpenAI expects.
# Each one maps to a Python function in tools.py.
# "parameters" describes what arguments the LLM should pass when calling the tool.
TOOLS = [
    {
        "type": "function",
        "function": {
            "name": "list_tables",
            "description": "List all tables in the data warehouse with row counts",
            "parameters": {"type": "object", "properties": {}, "required": []},
        },
    },
    {
        "type": "function",
        "function": {
            "name": "describe_table",
            "description": "Get column names and types for a specific table",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Fully qualified table name (e.g. marts.fct_orders)",
                    }
                },
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "sample_data",
            "description": "Get a few example rows from a table to see actual values",
            "parameters": {
                "type": "object",
                "properties": {
                    "table_name": {
                        "type": "string",
                        "description": "Fully qualified table name (e.g. marts.fct_orders)",
                    }
                },
                "required": ["table_name"],
            },
        },
    },
    {
        "type": "function",
        "function": {
            "name": "run_sql",
            "description": "Execute a SQL query against the DuckDB warehouse and return results",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string",
                        "description": "A SELECT SQL query using DuckDB syntax",
                    }
                },
                "required": ["query"],
            },
        },
    },
]

EXPLAIN_PROMPT = """Review how an AI agent answered a data question.
Only mention things the user might not realize from looking at the SQL:
- Implicit assumptions (e.g. "includes all statuses, not just completed")
- Aggregation choices (e.g. "averaged per order, not per customer")
- Missing filters (e.g. "no date range applied")
If the query is straightforward with no hidden assumptions, say "Straightforward query — no assumptions to flag."
One sentence max. Do not restate the SQL."""


def chat(messages):
    """Send messages to the LLM with tools enabled. Returns the response message.
    The response is either a text answer or one or more tool calls."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )
    return response.choices[0].message


def explain(question, trace, answer):
    """Second LLM call that explains the agent's reasoning process to the user."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {"role": "system", "content": EXPLAIN_PROMPT},
            {"role": "user", "content": f"Question: {question}\n\nTrace:\n{trace}\n\nAnswer: {answer}"},
        ],
    )
    return response.choices[0].message.content
