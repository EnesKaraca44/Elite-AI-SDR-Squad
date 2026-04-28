import os
import google.generativeai as genai
from typing import Dict
from dotenv import load_dotenv

load_dotenv()

class OutreachAgent:
    """Expert Outreach Agent generating high-conversion messages using Gemini."""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-flash-latest')
        print("OutreachAgent Initialized with gemini-flash-latest")

    def generate(self, analysis: Dict, contacts_data: Dict = None) -> Dict:
        """Generate tailored outreach based on strategic gaps."""
        
        contacts_context = ""
        if contacts_data and contacts_data.get('contacts'):
            c = contacts_data['contacts'][0]
            contacts_context = f"\nTarget Decision Maker: {c.get('first_name') or ''} {c.get('last_name') or ''} ({c.get('position') or 'Executive'}) - Email: {c.get('email') or 'Unknown'}"
            
        prompt = f"""
        You are a World-Class Sales Copywriter.
        Based on this analysis: {analysis.get('roi_prediction')} 
        and these gaps: {analysis.get('strategic_gaps')},
        {contacts_context}
        
        Create two personalized outreach messages directed at the 'Target Decision Maker' (if provided, otherwise general):
        1. LinkedIn Connection Request (under 300 chars)
        2. Cold Email (Short, value-focused)
        
        Output should be clear and concise.
        """
        
        import time
        for attempt in range(3):
            try:
                print(f"OutreachAgent: Generating content (Attempt {attempt+1})...")
                response = self.model.generate_content(
                    prompt,
                    safety_settings=[
                        {"category": "HARM_CATEGORY_HARASSMENT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_HATE_SPEECH", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_SEXUALLY_EXPLICIT", "threshold": "BLOCK_NONE"},
                        {"category": "HARM_CATEGORY_DANGEROUS_CONTENT", "threshold": "BLOCK_NONE"}
                    ]
                )
                content = response.text
                print("OutreachAgent: Success.")
                return {
                    "outreach_drafts": content
                }
            except Exception as e:
                if "429" in str(e):
                    wait_time = 35
                    print(f"OutreachAgent: Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"OutreachAgent ERROR: {str(e)}")
                    return {"error": str(e)}
        return {"error": "Outreach failed: Max retries exceeded due to rate limits."}
