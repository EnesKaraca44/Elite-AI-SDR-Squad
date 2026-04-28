import os
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
model = genai.GenerativeModel('gemini-1.5-flash-latest')

try:
    response = model.generate_content("Hi")
    print("SUCCESS:", response.text)
except Exception as e:
    print("FAILED:", str(e))
