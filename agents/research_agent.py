import os
import requests
from typing import Dict, List
from dotenv import load_dotenv

load_dotenv()

class ResearchAgent:
    """Elite Research Agent using Serper and Perplexity for multi-source intelligence."""
    
    def __init__(self):
        self.serper_key = os.getenv("SERPER_API_KEY")
        self.perplexity_key = os.getenv("PERPLEXITY_API_KEY")

    def get_real_time_news(self, company_name: str) -> str:
        """Fetch latest news using Gemini (Free) as a fallback if Perplexity is missing."""
        if self.perplexity_key:
            url = "https://api.perplexity.ai/chat/completions"
            payload = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "system", "content": "You are a real-time news researcher. Provide the most recent news (last 24h-7d) about the company. Be concise."},
                    {"role": "user", "content": f"Find recent news about {company_name}"}
                ]
            }
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            try:
                response = requests.post(url, json=payload, headers=headers)
                return response.json()['choices'][0]['message']['content']
            except Exception:
                pass # Fallback to Gemini if request fails
            
        # Free Gemini Fallback for News/Insights
        import google.generativeai as genai
        try:
            genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
            model = genai.GenerativeModel('gemini-flash-latest')
            print("ResearchAgent: Using Gemini News Fallback...")
            response = model.generate_content(f"Provide a concise summary of the latest news and market position for {company_name} from the last 7 days.")
            print("ResearchAgent: Gemini News Success.")
            return response.text
        except Exception as e:
            return f"News search failed: {str(e)}"

    def deep_crawl(self, domain: str) -> str:
        """Advanced website crawling using Trafilatura for elite free text extraction."""
        import trafilatura
        
        if not domain.startswith("http"):
            url = f"https://{domain}"
        else:
            url = domain

        try:
            downloaded = trafilatura.fetch_url(url)
            if downloaded is None:
                # Fallback to basic scraper if blocked or failed
                from researcher import Researcher
                return Researcher().scrape_website(url)
            
            result = trafilatura.extract(downloaded, include_comments=False, include_tables=True, no_fallback=False)
            return result[:8000] if result else "No content extracted."
        except Exception as e:
            return f"Scraping failed: {str(e)}"

    def execute(self, company_name: str, domain: str) -> Dict:
        return {
            "news": self.get_real_time_news(company_name),
            "site_content": self.deep_crawl(domain),
            "search_logs": f"Executed deep crawl on {domain} and real-time news search for {company_name}."
        }
