import json
from cli.db import get_connection
from cli.llm import chat, SYSTEM_PROMPT
from cli.tools import list_tables, describe_table, run_sql


def execute_tool(conn, name, args):
    """Route a tool call from the LLM to the matching Python function."""
    if name == "list_tables":
        return list_tables(conn)
    elif name == "describe_table":
        return describe_table(conn, args["table_name"])
    elif name == "run_sql":
        return run_sql(conn, args["query"])
    else:
        return {"error": f"Unknown tool: {name}"}


def log_tool(name, args, result):
    """Print what the agent is doing so the user can follow along."""
    if name == "run_sql":
        print(f"  → {name}")
        for line in args["query"].strip().split("\n"):
            print(f"    {line}")
    else:
        print(f"  → {name}({json.dumps(args)})")

    preview = json.dumps(result, default=str)
    if len(preview) > 150:
        preview = preview[:150] + "..."
    print(f"  ← {preview}\n")


def main():
    conn = get_connection()
    print("Connected to warehouse. Ask a question (type 'exit' to quit).\n")

    while True:
        question = input("> ").strip()
        if not question:
            continue
        if question.lower() == "exit":
            break

        messages = [
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": question},
        ]

        # Agent loop: LLM responds with either text (done) or tool calls (keep going)
        while True:
            response = chat(messages)

            if not response.tool_calls:
                print(f"\n{response.content}\n")
                break

            messages.append(response)
            for tool_call in response.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                try:
                    result = execute_tool(conn, name, args)
                except Exception as e:
                    result = {"error": str(e)}

                log_tool(name, args, result)

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })

    conn.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()
