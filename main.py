import json
import logging

from parser import analyze_sql
from gemini_llm import get_sql_json_from_llm
from export_brd import export_to_excel
from logger_config import setup_logger

setup_logger()
logger = logging.getLogger(__name__)


def generate_brd(sql_file):
    logger.info("Starting BRD generation")

    with open(sql_file, "r") as file:
        sql_text = file.read()

    logger.info("SQL file loaded")

    analysis = analyze_sql(sql_text)
    logger.info("SQL analysis completed")

    llm_response = get_sql_json_from_llm(sql_text)
    logger.info("Received response from LLM")

    try:
        brd_json = json.loads(llm_response)
        logger.info("LLM JSON parsed successfully")
    except json.JSONDecodeError:
        logger.error("Failed to parse LLM JSON")
        return

    export_to_excel(brd_json, filename="BRD_Output.xlsx")
    logger.info("BRD Excel generated successfully")


if __name__ == "__main__":
    generate_brd("sample.sql")
