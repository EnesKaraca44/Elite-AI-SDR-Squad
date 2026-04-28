import os
import google.generativeai as genai
import time
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

models_to_try = [
    'gemini-2.0-flash',
    'gemini-1.5-flash',
    'gemini-1.5-flash-8b'
]

for model_name in models_to_try:
    print(f"--- Testing {model_name} ---")
    try:
        model = genai.GenerativeModel(model_name)
        response = model.generate_content("Say 'success'")
        print(f"RESULT: {response.text}")
    except Exception as e:
        print(f"ERROR: {str(e)}")
    print("Waiting 10s...")
    time.sleep(10)
