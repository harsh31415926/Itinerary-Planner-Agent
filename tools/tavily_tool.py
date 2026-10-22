from tavily import TavilyClient
import os 
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TAVILY_API_KEY")

def tavily_search(query:str) -> str:
    if not API_KEY:
        raise RuntimeError("TAVILY_API_KEY is not configured")

    response = TavilyClient(api_key=API_KEY).search(query=query, max_results=5)
    if not isinstance(response, dict):
        raise RuntimeError("Tavily returned an invalid search response")

    results = []

    raw_results = response.get("results", [])
    if not isinstance(raw_results, list):
        raise RuntimeError("Tavily returned malformed search results")

    for i, r in enumerate(raw_results, 1):
        if not isinstance(r, dict):
            continue
        title = r.get('title') or 'Untitled source'
        url = r.get('url') or ''
        snippet = (r.get('content') or '').strip()

        if len(snippet) > 260:
            snippet = snippet[:260].rsplit(" ", 1)[0] + "…"
        
        results.append(f"{i}. {title}\nSource: {url or 'not provided'}\nEvidence: {snippet or 'No descriptive excerpt returned.'}")
    
    return '\n\n'.join(results) if results else "No hotel found"

# res = tavily_search("top luxury hotels in NYC with ratings and prices")
# print(res)
