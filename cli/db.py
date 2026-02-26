from pathlib import Path
import duckdb

WAREHOUSE_PATH = Path(__file__).parent.parent / "warehouse" / "data.duckdb"


def get_connection():
    """Open a read-only connection to the DuckDB warehouse."""
    return duckdb.connect(str(WAREHOUSE_PATH), read_only=True)


def run_query(conn, sql):
    """Execute a SQL query and return results as a list of dicts."""
    result = conn.execute(sql)
    # result.description is a list of (name, type, ...) tuples per column
    # https://peps.python.org/pep-0249/#description
    columns = [desc[0] for desc in result.description]
    rows = result.fetchall()
    return [dict(zip(columns, row)) for row in rows]
