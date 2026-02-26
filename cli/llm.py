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
3. Call run_sql to query the data
4. Provide a clear, concise answer with specific numbers

Rules:
- Always qualify table names with the schema (e.g. marts.fct_orders)
- Use DuckDB SQL syntax
- Only write SELECT queries
- Today's date is {date.today().isoformat()}"""

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


def chat(messages):
    """Send messages to the LLM with tools enabled. Returns the response message.
    The response is either a text answer or one or more tool calls."""
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        tools=TOOLS,
    )
    return response.choices[0].message
