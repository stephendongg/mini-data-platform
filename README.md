# Mini Data Platform — CLI Agent

A CLI agent that answers ad-hoc analytical questions against a DuckDB warehouse. Uses OpenAI function calling to let the LLM explore the database schema and run SQL queries autonomously.

## Quick Start

```bash
./setup.sh                          # Generate data, run pipeline
export OPENAI_API_KEY=sk-...        # Set your API key
uv run python -m cli.main           # Start the agent
```

## How It Works

The LLM has three tools it can call in a loop until it has enough info to answer:

1. `list_tables` — see what tables exist and their row counts
2. `describe_table` — get column names and types for a table
3. `run_sql` — execute a read-only SQL query

## Architecture

```
cli/
  db.py       # Read-only DuckDB connection and query execution
  tools.py    # Tool functions: list_tables, describe_table, run_sql
  llm.py      # OpenAI function calling setup and tool definitions
  main.py     # Agent loop that routes tool calls until the LLM answers
```

## Design Decisions

- **Read-only DuckDB** — Safety guarantee at the database level
- **Runtime schema discovery** — No hardcoded table or column names
- **Marts schema only** — Queries the clean, analytics-ready layer
- **GPT-4o-mini** — Fast, cheap, accurate enough for SQL generation

## What's Next

- Multi-turn memory (follow-up questions)
- Configurable data source (any DuckDB path/schema)
- Sample data tool (let the LLM peek at rows)

See [instructions/README.md](instructions/README.md) for the original assignment.
