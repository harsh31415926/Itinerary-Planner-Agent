from tavily import TavilyClient
import os 
import requests
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("TAVILY_API_KEY")

client = TavilyClient(api_key=API_KEY)

def tavily_search(query:str) -> str:

    response= client.search(query = query , max_results = 7)

    results = []

    for i , r in enumerate(response['results'] ,1 ):
        title = r.get('title' , 'unknown')
        url = r.get('url', 'unknown')
        snippet = r.get('content', '').strip()

        if len(snippet) > 377:
            snippet = snippet[:377].rsplit(" " , 1)[0] + '...'
            
            """ 
            s = 'this is a very good movie.
            s[:24] = 'this is a very good mov'
            s[:24].rsplit() = [this is a very good mov , ie]
            s[:24].rsplit('' ,1) = this is a very good 
            
            # deletes the incomplete word
            """
        
        results.append(f''' {i}.**{title}**\n {url}\n {snippet}''')
    
    return '\n\n'.join(results) if results else "No hotel found"

# res = tavily_search("top luxury hotels in NYC with ratings and prices")
# print(res)