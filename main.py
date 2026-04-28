import sys
import json
import os
from researcher import Researcher
from analyzer import Analyzer
from dotenv import load_dotenv

load_dotenv()

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "No company name or URL provided."}))
        return

    company_input = sys.argv[1]
    
    # Initialize tools
    researcher = Researcher()
    analyzer = Analyzer()

    # Phase 1: Research
    search_results = researcher.search_company(company_input)
    search_text = "\n".join([f"{r.get('title')}: {r.get('snippet')}" for r in search_results])
    
    # Try to extract URL from search results if input is just a name
    url = company_input
    if not url.startswith("http") and "." not in url:
        if search_results:
            url = search_results[0].get("link", "")
    
    # Phase 2: Scrape
    scraped_data = researcher.scrape_website(url) if url else ""

    # Phase 3: Analyze
    analysis = analyzer.analyze(company_input, scraped_data, search_text)

    if analysis:
        print(analysis.json())
    else:
        print(json.dumps({"error": "Analysis failed."}))

if __name__ == "__main__":
    main()
