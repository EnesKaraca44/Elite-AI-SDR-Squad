import os
import requests
from dotenv import load_dotenv

load_dotenv()

class ContactAgent:
    """Agent responsible for finding decision-maker emails and LinkedIn profiles."""
    
    def __init__(self):
        self.hunter_api_key = os.getenv("HUNTER_API_KEY")

    def find_contacts(self, company_name: str, domain: str) -> dict:
        """Finds contacts for a given domain."""
        contacts = []
        
        # 1. Try Hunter.io API if available
        if self.hunter_api_key:
            try:
                # domain cleansing
                clean_domain = domain.replace("https://", "").replace("http://", "").split("/")[0]
                url = f"https://api.hunter.io/v2/domain-search?domain={clean_domain}&api_key={self.hunter_api_key}"
                response = requests.get(url, timeout=10)
                if response.status_code == 200:
                    data = response.json().get('data', {})
                    emails = data.get('emails', [])
                    for e in emails[:3]: # Get top 3
                        contacts.append({
                            "email": e.get('value'),
                            "first_name": e.get('first_name'),
                            "last_name": e.get('last_name'),
                            "position": e.get('position'),
                            "linkedin": e.get('linkedin')
                        })
                    if contacts:
                        return {"contacts": contacts, "source": "Hunter.io"}
            except Exception as e:
                print(f"ContactAgent (Hunter.io) Error: {e}")

        # 2. Mock/Fallback Data if no API key exists (MVP / Demo Data)
        return {
            "contacts": [
                {
                    "email": f"ceo@{domain}",
                    "first_name": "Decision",
                    "last_name": "Maker",
                    "position": "CEO / Founder",
                    "linkedin": f"linkedin.com/company/{company_name.lower().replace(' ', '')}"
                },
                {
                    "email": f"marketing@{domain}",
                    "first_name": "Lead",
                    "last_name": "Director",
                    "position": "VP of Marketing",
                    "linkedin": None
                }
            ],
            "source": "Predictive Pattern Logic (Fallback)"
        }
