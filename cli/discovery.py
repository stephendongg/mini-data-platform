from cli.db import run_query

SCHEMA = "marts"  # only discover the clean, analytics-ready layer


def discover_schema(conn):
    """Query the database's built-in metadata tables (information_schema) to
    build a text description of all tables and columns for the LLM prompt.

    Returns a string like:
        Table: marts.fct_orders (35,980 rows)
          transaction_id (VARCHAR)
          transaction_date (DATE)
          ...
    """

    tables = run_query(conn, f"""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = '{SCHEMA}'
        ORDER BY table_name
    """)

    lines = []
    for table in tables:
        table_name = table["table_name"]
        qualified = f"{SCHEMA}.{table_name}"

        count = run_query(conn, f"SELECT COUNT(*) as n FROM {qualified}")[0]["n"]
        lines.append(f"\nTable: {qualified} ({count:,} rows)")

        columns = run_query(conn, f"""
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = '{SCHEMA}' AND table_name = '{table_name}'
            ORDER BY ordinal_position
        """)

        for col in columns:
            lines.append(f"  {col['column_name']} ({col['data_type']})")

    return "\n".join(lines)
