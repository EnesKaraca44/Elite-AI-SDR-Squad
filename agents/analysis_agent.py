import os
import json
from typing import Dict
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

class AnalysisAgent:
    """Financial & Strategic Analysis Agent using Google Gemini."""
    
    def __init__(self):
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-flash-latest')
        print("AnalysisAgent Initialized with gemini-flash-latest")

    def analyze(self, research_data: Dict) -> Dict:
        system_prompt = """
        You are an Elite Financial & Strategic Analyst.
        Your goal is to perform a deep-dive analysis on a company based on raw research.
        You must output ONLY valid JSON.
        Focus on:
        - Financial Health (Simulated from news/site)
        - Strategic Gaps
        - ROI Potential for the client
        - Market Position (Tier 1/2/3)
        """
        
        user_prompt = f"""
        Analyze this research:
        {json.dumps(research_data)}
        
        Output structure:
        {{
            "financial_score": 0-100,
            "strategic_gaps": ["gap1", "gap2"],
            "roi_prediction": "concise string",
            "market_position": "Tier 1/2/3",
            "critical_news_impact": "string"
        }}
        """
        
        import time
        for attempt in range(3):
            try:
                print(f"AnalysisAgent: Generating content for {research_data.get('company_name')} (Attempt {attempt+1})...")
                response = self.model.generate_content(
                    f"{system_prompt}\n\n{user_prompt}",
                    generation_config=genai.types.GenerationConfig(
                        response_mime_type="application/json",
                    )
                )
                data = json.loads(response.text)
                print("AnalysisAgent: Success.")
                return data
            except Exception as e:
                if "429" in str(e):
                    wait_time = 35 # Gemini Free Tier wait
                    print(f"AnalysisAgent: Rate limited. Retrying in {wait_time}s...")
                    time.sleep(wait_time)
                else:
                    print(f"AnalysisAgent ERROR: {str(e)}")
                    return {"error": f"Analysis failed: {str(e)}"}
        return {"error": "Analysis failed: Max retries exceeded due to rate limits."}
