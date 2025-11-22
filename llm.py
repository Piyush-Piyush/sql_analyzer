from dotenv import load_dotenv
import os
from google import genai
from google.genai import types

load_dotenv()

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def explain_sql(sql_text):
    model = genai.GenerativeModel("gemini-3-pro-preview")
    prompt = f"""
    Analyze this SQL and explain the business meaning:

    {sql_text}

    Provide:
    - High-level purpose
    - Data flow
    - Business rules
    """
    response = model.generate_content(prompt)
    return response.text
