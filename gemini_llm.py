# gemini_llm.py
import os
import logging
from dotenv import load_dotenv
from google import genai
from google.genai import types
from google.genai.errors import APIError

logger = logging.getLogger(__name__)

load_dotenv()

api_key = os.environ.get("GEMINI_API_KEY")
gemini_model = "gemini-2.5-flash"


# -------------------------
# RESPONSE SCHEMA DEFINITION
# -------------------------
def define_response_schema() -> types.Schema:
    string_field = types.Schema(type=types.Type.STRING)

    join_item_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Left Table": string_field,
            "Right Table": string_field,
            "Join Type": string_field,
            "Condition": string_field,
        }
    )

    filter_item_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Column": string_field,
            "Operator": string_field,
            "Value": string_field,
        }
    )

    transform_item_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Output Column": string_field,
            "Expression": string_field,
        }
    )

    dependency_item_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Column": string_field,
            "Depends On": types.Schema(
                type=types.Type.ARRAY,
                items=string_field
            ),
        }
    )

    bq_column_item_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Table": string_field,
            "Column": string_field,
            "Data Type": string_field,
        }
    )

    bq_summary_schema = types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Tables to Migrate": types.Schema(type=types.Type.ARRAY, items=string_field),
            "Columns to Migrate": types.Schema(type=types.Type.ARRAY, items=bq_column_item_schema),
            "PrimaryKey_ForeignKey Dependencies": types.Schema(type=types.Type.ARRAY, items=string_field),
            "Lookup_Reference Tables Needed": types.Schema(type=types.Type.ARRAY, items=string_field),
            "Transformations Handled in BigQuery": types.Schema(type=types.Type.ARRAY, items=string_field),
        }
    )

    return types.Schema(
        type=types.Type.OBJECT,
        properties={
            "Section 1 — Tables Needed": types.Schema(type=types.Type.ARRAY, items=string_field),
            "Section 2 — Columns Needed": types.Schema(type=types.Type.ARRAY, items=string_field),
            "Section 3 — Joins": types.Schema(type=types.Type.ARRAY, items=join_item_schema),
            "Section 4 — Filters": types.Schema(type=types.Type.ARRAY, items=filter_item_schema),
            "Section 5 — Transformations": types.Schema(type=types.Type.ARRAY, items=transform_item_schema),
            "Section 6 — Data Dependencies": types.Schema(type=types.Type.ARRAY, items=dependency_item_schema),
            "Section 7 — BigQuery Requirements Summary": bq_summary_schema,
        },
        required=[
            "Section 1 — Tables Needed",
            "Section 2 — Columns Needed",
            "Section 3 — Joins",
            "Section 4 — Filters",
            "Section 5 — Transformations",
            "Section 6 — Data Dependencies",
            "Section 7 — BigQuery Requirements Summary",
        ]
    )


# -------------------------
# LLM CALL
# -------------------------
def get_sql_json_from_llm(sql_text: str, model_name: str = gemini_model) -> str:
    if not api_key:
        logger.error("GEMINI_API_KEY not found in environment")
        return ""

    if not sql_text:
        logger.error("Empty SQL input received")
        return ""

    logger.info("Preparing prompt for Gemini LLM")

    prompt = f"""
You are an expert Data Architect and SQL Analyst.

Your task is to analyze the given SQL query and extract all information required
to recreate the report during a database migration to BigQuery.

Your output MUST strictly follow the provided JSON schema.
Do NOT add explanations or extra text outside the JSON.

SQL QUERY:
{sql_text}
"""

    try:
        logger.info("Initializing Gemini client")
        client = genai.Client(api_key=api_key)

        logger.info("Sending request to Gemini with strict schema enforcement")
        response = client.models.generate_content(
            model=model_name,
            contents=[prompt],
            config=types.GenerateContentConfig(
                temperature=0.0,
                response_mime_type="application/json",
                response_schema=define_response_schema()
            )
        )

        logger.info("Gemini response received successfully")
        logger.debug(f"Raw Gemini response:\n{response.text}")

        return response.text

    except APIError:
        logger.exception("Gemini API error occurred")
        return ""

    except Exception:
        logger.exception("Unexpected error while calling Gemini")
        return ""
