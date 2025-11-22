import os
from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
gemini_model = "gemini-2.5-flash"


def explain_sql(sql_text: str, model_name: str = gemini_model) -> str:
    if not api_key:
        return ("ERROR: GEMINI_API_KEY environment variable not found. "
                "Please set it to your actual Gemini API key.")

    if not sql_text:
        return "ERROR: No SQL text present."

    
    prompt = f"""
                You are an expert Data Architect and SQL Analyst.

                Your task is to read a SQL query and extract ALL information required to recreate the report during a database migration to BigQuery.

                Your output MUST be returned STRICTLY in the following JSON format — with:
                - No text outside the JSON
                - No additional keys
                - No changes to structure or nesting

                {{
                    "Section 1 — Tables Needed": [
                        "table1",
                        "table2",
                        "table3"
                    ],

                    "Section 2 — Columns Needed": [
                        "table1.colA",
                        "table1.colB",
                        "table2.colX"
                    ],

                    "Section 3 — Joins": [
                        {{
                            "Left Table": "table1 t1",
                            "Right Table": "table2 t2",
                            "Join Type": "INNER",
                            "Condition": "t1.id = t2.id"
                        }},
                        {{
                            "Left Table": "table2 t2",
                            "Right Table": "table3 t3",
                            "Join Type": "LEFT",
                            "Condition": "t2.key = t3.key"
                        }}
                    ],

                    "Section 4 — Filters": [
                        {{
                            "Column": "t1.status",
                            "Operator": "=",
                            "Value": "'ACTIVE'"
                        }},
                        {{
                            "Column": "t2.amount",
                            "Operator": ">",
                            "Value": "100"
                        }}
                    ],

                    "Section 5 — Transformations": [
                        {{
                            "Output Column": "clean_date",
                            "Expression": "PARSE_DATE('%Y-%m-%d', raw_date)"
                        }},
                        {{
                            "Output Column": "amount_usd",
                            "Expression": "amount * exchange_rate"
                        }}
                    ],

                    "Section 6 — Data Dependencies": [
                        {{
                            "Column": "amount_usd",
                            "Depends On": ["amount", "exchange_rate"]
                        }},
                        {{
                            "Column": "clean_date",
                            "Depends On": ["raw_date"]
                        }}
                    ],

                    "Section 7 — BigQuery Requirements Summary": {{
                        "Tables to Migrate": [
                            "table1",
                            "table2",
                            "table3"
                        ],

                        "Columns to Migrate": [
                            {{
                                "Table": "table1",
                                "Column": "id",
                                "Data Type": "INT64"
                            }},
                            {{
                                "Table": "table2",
                                "Column": "amount",
                                "Data Type": "FLOAT64"
                            }}
                        ],

                        "PrimaryKey_ForeignKey Dependencies": [
                            "table1.id → table2.id",
                            "table2.key → table3.key"
                        ],

                        "Lookup_Reference Tables Needed": [
                            "country_lookup",
                            "status_lookup"
                        ],

                        "Transformations Handled in BigQuery": [
                            "convert date formats",
                            "standardize country codes",
                            "derive USD amounts"
                        ]
                    }}
                }}

                Strict Rules:
                - Do NOT add explanations outside the JSON.
                - Do NOT modify the JSON structure.
                - Do NOT add or rename fields.

                Now analyze the following SQL query and return ONLY the JSON:

                {sql_text}
            """

    try:
        client = genai.Client(api_key=api_key)

        print(f"------ Sending prompt to {model_name}... ------")

        response = client.models.generate_content(
            model=model_name,
            contents=[prompt]
        )

        print("------ Received response. ------")
        return response.text

    except APIError as e:
        return f"ERROR: API error occurred: {e}"
    except Exception as e:
        return f"ERROR: Unexpected error occurred: {e}"


if __name__ == "__main__":
    sample_sql = """
        SELECT order_id, order_date, customer_id
        FROM orders
        WHERE order_date > '2022-01-01'
          AND order_date < '2022-02-01'
          AND customer_id = '12345';
    """

    json_output = explain_sql(sample_sql)

    print("\n------ JSON Output ------")
    print(json_output)
    print("-------------------------")
