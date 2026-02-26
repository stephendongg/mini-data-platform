import json
import textwrap
import uuid
from datetime import datetime
from pathlib import Path
from cli.db import get_connection
from cli.llm import chat, explain, SYSTEM_PROMPT
from cli.tools import list_tables, describe_table, sample_data, run_sql

MAX_TURNS = 10
LOG_PATH = Path(__file__).parent.parent / "logs"


def execute_tool(conn, name, args):
    """Route a tool call from the LLM to the matching Python function."""
    if name == "list_tables":
        return list_tables(conn)
    elif name == "describe_table":
        return describe_table(conn, args["table_name"])
    elif name == "sample_data":
        return sample_data(conn, args["table_name"])
    elif name == "run_sql":
        return run_sql(conn, args["query"])
    else:
        return {"error": f"Unknown tool: {name}"}


def format_step(num, name, args, result):
    """Format a tool call as a readable one-liner for the user."""
    if name == "list_tables":
        tables = [r["table"] for r in result] if isinstance(result, list) else []
        return f"  {num}. Listed tables: {', '.join(tables)}"
    elif name == "describe_table":
        cols = len(result) if isinstance(result, list) else 0
        return f"  {num}. Described {args['table_name']} → {cols} columns"
    elif name == "sample_data":
        rows = len(result) if isinstance(result, list) else 0
        return f"  {num}. Sampled {rows} rows from {args['table_name']}"
    elif name == "run_sql":
        sql = args["query"].replace("\n", " ").strip()
        return f"  {num}. SQL: {sql}"
    return f"  {num}. {name}"


def print_result(question, trace, answer):
    """Print the answer and reasoning, then save to log file."""
    indented_answer = textwrap.indent(answer, "  ")
    print(f"\n  ── Answer ──\n{indented_answer}")

    reasoning = explain(question, "\n".join(trace), answer)
    wrapped = textwrap.fill(reasoning, width=70, initial_indent="  ", subsequent_indent="  ")
    print(f"\n  ── Reasoning ──\n{wrapped}\n")

    return reasoning


def save_log(interaction_id, question, trace, answer, reasoning):
    """Save the full trace as a JSON file with the interaction ID."""
    LOG_PATH.mkdir(exist_ok=True)
    entry = {
        "id": interaction_id,
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "trace": trace,
        "answer": answer,
        "reasoning": reasoning,
    }
    filepath = LOG_PATH / f"{interaction_id}.json"
    with open(filepath, "w") as f:
        json.dump(entry, f, indent=2, default=str)


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

        interaction_id = str(uuid.uuid4())
        step_num = 0
        trace = []
        full_trace = []
        print(f"\n  Interaction: {interaction_id}\n\n  ── Actions ──")

        for _ in range(MAX_TURNS):
            response = chat(messages)

            if not response.tool_calls:
                reasoning = print_result(question, trace, response.content)
                save_log(interaction_id, question, full_trace, response.content, reasoning)
                break

            messages.append(response)
            for tool_call in response.tool_calls:
                name = tool_call.function.name
                args = json.loads(tool_call.function.arguments)

                try:
                    result = execute_tool(conn, name, args)
                except Exception as e:
                    result = {"error": str(e)}

                step_num += 1
                step = format_step(step_num, name, args, result)
                print(step)
                trace.append(step.strip())
                full_trace.append({"tool": name, "args": args, "result": result})

                messages.append({
                    "role": "tool",
                    "tool_call_id": tool_call.id,
                    "content": json.dumps(result, default=str),
                })

    conn.close()
    print("Goodbye!")


if __name__ == "__main__":
    main()
