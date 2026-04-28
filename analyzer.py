import os
import json
from typing import Dict, Optional
import requests
from dotenv import load_dotenv
from pydantic import BaseModel, Field

load_dotenv()

class CompanyAnalysis(BaseModel):
    company_name: str
    industry: str
    summary: str
    score: int = Field(..., ge=0, le=100)
    reasons: list[str]
    potential_pain_points: list[str]
    suggested_pitch: str

class Analyzer:
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.api_url = "https://api.openai.com/v1/chat/completions"

    def analyze(self, company_name: str, scraped_data: str, search_results: str) -> Optional[CompanyAnalysis]:
        """Analyze company data using OpenAI to generate a score and rapport."""
        if not self.api_key:
            print("Error: OPENAI_API_KEY not found.")
            return None

        prompt = f"""
        Analyze the following company data and provide a detailed lead scoring report.
        
        Company Name: {company_name}
        
        --- SCRAPED WEBSITE DATA ---
        {scraped_data}
        
        --- SEARCH RESULTS ---
        {search_results}
        
        --- INSTRUCTIONS ---
        1. Identify the industry and core business model.
        2. Assign a score (0-100) based on perceived market value and growth potential.
        3. Identify 3 key reasons for this score.
        4. Identify potential pain points this company might face.
        5. Write a personalized 2-sentence sales pitch.
        
        Respond ONLY with a valid JSON object matching this structure:
        {{
            "company_name": "...",
            "industry": "...",
            "summary": "...",
            "score": 85,
            "reasons": ["...", "...", "..."],
            "potential_pain_points": ["...", "..."],
            "suggested_pitch": "..."
        }}
        """

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        data = {
            "model": "gpt-4-turbo-preview",
            "messages": [
                {"role": "system", "content": "You are a senior B2B sales strategist and market researcher."},
                {"role": "user", "content": prompt}
            ],
            "response_format": { "type": "json_object" }
        }

        try:
            response = requests.post(self.api_url, headers=headers, json=data)
            response.raise_for_status()
            result_json = response.json()["choices"][0]["message"]["content"]
            return CompanyAnalysis.parse_raw(result_json)
        except Exception as e:
            print(f"Error during analysis: {e}")
            return None

if __name__ == "__main__":
    analyzer = Analyzer()
    # Test would go here
