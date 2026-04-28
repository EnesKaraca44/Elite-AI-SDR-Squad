import requests
from bs4 import BeautifulSoup
import os
from typing import Dict, List, Optional
from dotenv import load_dotenv

load_dotenv()

class Researcher:
    def __init__(self, serper_api_key: Optional[str] = None):
        self.serper_api_key = serper_api_key or os.getenv("SERPER_API_KEY")
        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36"
        }

    def search_company(self, company_name: str) -> List[Dict]:
        """Search for company information using Serper.dev."""
        if not self.serper_api_key:
            print("Warning: SERPER_API_KEY not found. Search skipped.")
            return []

        url = "https://google.serper.dev/search"
        payload = {
            "q": f"{company_name} company overview mission products",
            "gl": "us",
            "hl": "en",
            "autocorrect": True
        }
        headers = {
            'X-API-KEY': self.serper_api_key,
            'Content-Type': 'application/json'
        }

        try:
            response = requests.post(url, headers=headers, json=payload)
            response.raise_for_status()
            results = response.json()
            return results.get("organic", [])
        except Exception as e:
            print(f"Error during search: {e}")
            return []

    def scrape_website(self, url: str) -> str:
        """Scrape text content from a website."""
        if not url.startswith("http"):
            url = f"https://{url}"

        try:
            response = requests.get(url, headers=self.headers, timeout=10)
            response.raise_for_status()
            soup = BeautifulSoup(response.text, 'html.parser')

            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()

            # Get text
            text = soup.get_text()

            # Clean up whitespace
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = '\n'.join(chunk for chunk in chunks if chunk)

            return text[:5000] # Limit to 5000 characters for LLM context
        except Exception as e:
            print(f"Error scraping {url}: {e}")
            return ""

if __name__ == "__main__":
    researcher = Researcher()
    # Test
    # print(researcher.scrape_website("https://openai.com"))
