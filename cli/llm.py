import os
from pathlib import Path
from dotenv import load_dotenv
from openai import OpenAI

load_dotenv(Path(__file__).parent.parent / ".env")

client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

# gpt-4o-mini over gpt-4o: fast and cheap, accurate enough for SQL generation prototype.
MODEL = "gpt-4o-mini"


def generate_sql(schema_context, question):
    """Send the schema and user question to the LLM, get back a SQL query."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": f"""You are an expert SQL analyst. Write a DuckDB SQL query to answer the user's question.

                Here is the database schema:
                {schema_context}

                Rules:
                - Write only SELECT queries
                - Always qualify table names with the schema (e.g. marts.fct_orders)
                - Use DuckDB SQL syntax
                - Return ONLY the SQL query, no explanation or markdown""",
            },
            {"role": "user", "content": question},
        ],
    )

    return response.choices[0].message.content.strip()


def summarize_results(question, sql, results):
    """Send query results back to the LLM for a plain-English summary.
    Separate from generate_sql so each call stays focused and failures can be retried independently."""

    response = client.chat.completions.create(
        model=MODEL,
        messages=[
            {
                "role": "system",
                "content": "You are a data analyst. Given a question, the SQL that was run, and the results, write a concise natural-language answer. Mention specific numbers.",
            },
            {
                "role": "user",
                "content": f"Question: {question}\n\nSQL: {sql}\n\nResults:\n{results}",
            },
        ],
    )

    return response.choices[0].message.content.strip()
