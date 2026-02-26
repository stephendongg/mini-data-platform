# Mini Data Platform — CLI Agent

A CLI agent that answers ad-hoc analytical questions against a DuckDB warehouse using LLM-generated SQL.

## Quick Start

```bash
./setup.sh                          # Generate data, run pipeline
export OPENAI_API_KEY=sk-...        # Set your API key
uv run python -m cli.main           # Start the agent
```

## How It Works

1. **Schema discovery** — On startup, queries `information_schema` to learn what tables and columns exist
2. **SQL generation** — Sends the schema + user question to GPT-4o-mini, gets back a SQL query
3. **Query execution** — Runs the SQL against DuckDB in read-only mode
4. **Summarization** — Sends results back to the LLM for a plain-English answer

## Architecture

```
cli/
  db.py            # Read-only DuckDB connection and query execution
  discovery.py     # Runtime schema introspection
  llm.py           # OpenAI API calls (SQL generation + summarization)
  main.py          # Interactive REPL that ties it all together
```

## Design Decisions

- **Read-only DuckDB** — Safety guarantee at the database level, no SQL parsing needed
- **Generic schema discovery** — No hardcoded table or column names; works on any DuckDB database
- **Marts schema only** — Queries the clean, analytics-ready layer rather than raw or staging
- **GPT-4o-mini** — Fast and cheap, accurate enough for SQL generation

## What's Next

This is an MVP. Planned improvements:

- **Retry logic** — Send SQL errors back to the LLM for self-correction
- **Sample values in discovery** — Show distinct values for categorical columns so the LLM writes more accurate queries
- **Multi-turn memory** — Support follow-up questions like "now break that down by category"
- **Configurable data source** — Accept any DuckDB path and schema as CLI arguments
- **Visualization** — Generate charts for trend-based questions

See [instructions/README.md](instructions/README.md) for the original assignment and data platform documentation.
