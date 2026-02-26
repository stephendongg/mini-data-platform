# Telescope

A CLI agent that answers ad-hoc analytical questions against a DuckDB warehouse. Uses OpenAI function calling to let the LLM explore the database schema and run SQL queries autonomously.

## Quick Start

```bash
./setup.sh                          # Generate data, run pipeline
export OPENAI_API_KEY=sk-...        # Set your API key
uv run python -m cli.main           # Start the agent
```

## Example

```
> What are the top 5 products by revenue?

  ── What are the top 5 products by revenue? ──
  Interaction: a3f1b2c4-...

  ── Actions ──
  1. Listed tables: marts.dim_customers, marts.dim_products, marts.fct_orders
  2. Described marts.fct_orders → 32 columns
  3. Described marts.dim_products → 10 columns
  4. SQL: SELECT p.product_name, SUM(o.total) AS revenue
         FROM marts.fct_orders o JOIN marts.dim_products p
         ON o.product_id = p.product_id
         GROUP BY p.product_name ORDER BY revenue DESC LIMIT 5

  ── Answer ──
  1. ValueCo Phone: $2,123,999
  2. ModernLine Laptop: $1,670,347
  3. ModernLine Smartwatch: $1,514,754
  4. EcoGoods Camera: $1,484,868
  5. Premium Headphones: $1,460,457

  ── Caveats ──
  Includes all order statuses, not just completed.
```

## How It Works

The LLM has four tools it can call in a loop until it has enough info to answer:

1. `list_tables` — see what tables exist and their row counts
2. `describe_table` — get column names and types for a table
3. `sample_data` — peek at example rows to see actual values
4. `run_sql` — execute a read-only SQL query (capped at 100 rows)

Each interaction outputs three sections: **Actions** (what the agent did), **Answer** (the result), and **Caveats** (assumptions flagged by a second LLM call). Full traces are saved to `logs/` as JSON files.

## Architecture

```
cli/
  db.py       # Read-only DuckDB connection and query execution
  tools.py    # Tool functions: list_tables, describe_table, sample_data, run_sql
  llm.py      # OpenAI function calling setup and tool definitions
  main.py     # Agent loop, structured output, and interaction logging
```

## Design Decisions

- **Read-only DuckDB** — Safety guarantee at the database level
- **Runtime schema discovery** — No hardcoded table or column names
- **Structured output** — Actions, answer, and caveats for interpretability
- **Interaction logging** — Full traces saved with UUIDs for debugging
- **Row limit on queries** — Caps results at 100 rows to prevent context overflow
- **GPT-4o-mini** — Fast, cheap, accurate enough for SQL generation

## What's Next

- Multi-turn memory (follow-up questions)
- Configurable data source (any DuckDB path/schema)
- Evals (automated test suite with known questions and expected answers)

See [instructions/README.md](instructions/README.md) for the original assignment.
