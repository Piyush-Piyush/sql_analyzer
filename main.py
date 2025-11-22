from parser import analyze_sql
from gemini_llm import explain_sql
from export_brd import export_to_excel


def generate_brd(sql_file):
    sql_text = open(sql_file).read()
    analysis = analyze_sql(sql_text)
    explanation = explain_sql(sql_text)

    export_to_excel(analysis, explanation)

if __name__ == "__main__":
    generate_brd("sample.sql")
