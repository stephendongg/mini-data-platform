from tabulate import tabulate
from cli.db import get_connection, run_query
from cli.discovery import discover_schema
from cli.llm import generate_sql, summarize_results


def main():
    # Startup: connect and learn the schema once
    conn = get_connection()
    schema_context = discover_schema(conn)
    print("Connected to warehouse. Ask a question (type 'exit' to quit).\n")

    while True:
        # Wait for user input
        question = input("> ").strip()
        if not question:
            continue
        if question.lower() == "exit":
            break

        # Step 1: Ask LLM to write SQL
        sql = generate_sql(schema_context, question)
        print(f"\n[SQL]\n{sql}\n")

        # Step 2: Run the SQL against DuckDB
        try:
            results = run_query(conn, sql)
        except Exception as e:
            print(f"[Error] {e}\n")
            continue

        if not results:
            print("[No results returned]\n")
            continue

        # Step 3: Show results as a table
        print("[Results]")
        print(tabulate(results, headers="keys", tablefmt="simple"))
        print()

        # Step 4: Ask LLM to summarize in plain English
        summary = summarize_results(question, sql, results)
        print(f"[Answer]\n{summary}\n")

    conn.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()
