import os 
from typing import TypedDict, Annotated
from pydantic import BaseModel
import operator 
import json
import logging
import re
import time

# import psycopg
from langgraph.graph import StateGraph , START , END
# from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (AnyMessage , HumanMessage , SystemMessage , AIMessage)

from langchain_openai import ChatOpenAI

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
OPENAI_MODEL = os.getenv("OPENAI_MODEL", "gpt-4.1-mini")

llm = ChatOpenAI(
    model=OPENAI_MODEL,
    api_key=OPENAI_API_KEY,
    temperature=0,
    max_retries=0,
)
logger = logging.getLogger(__name__)


def invoke_llm_with_rate_limit_retry(callable_, *args, **kwargs):
    """Retry short-lived provider rate limits, then let failures surface."""
    for attempt in range(3):
        try:
            return callable_(*args, **kwargs)
        except Exception as exc:
            if getattr(exc, "status_code", None) != 429 or attempt == 2:
                raise

            headers = getattr(getattr(exc, "response", None), "headers", {}) or {}
            reset = headers.get("x-ratelimit-reset-tokens") or headers.get("retry-after")
            delay = None
            if reset:
                match = re.search(r"\d+(?:\.\d+)?", str(reset))
                if match:
                    delay = float(match.group())
                    if str(reset).strip().lower().endswith("ms"):
                        delay /= 1000
            delay = min(max(delay if delay is not None else 2 ** (attempt + 1), 1), 30)
            logger.warning("LLM rate limit reached; retrying in %.1f seconds (attempt %s/3)", delay, attempt + 2)
            time.sleep(delay)

class TripInfo(BaseModel):
    destination: str | None = None
    destination_iata: str | None = None
    origin: str | None = None
    origin_iata: str | None = None
    duration: int | None = None
    budget: str | None = None
    start_date: str | None = None


''' ===================================================================== '''

class TravelState(TypedDict):

    user_query : str
    messages : Annotated[list[AnyMessage] , operator.add]

    destination: str
    destination_iata: str
    origin : str 
    origin_iata : str
    budget: str
    duration : int
    start_date:str

    flight_result : str
    hotel_result : str
    itinerary: str
    final_response: str
    clarification: str
    llm_calls: int







''' ========================================== '''



def parser_agent(state: TravelState):

    query = state["user_query"]
    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or api_key.lower() in {"put_your_openai_api_key_here", "your_openai_api_key"}:
        raise RuntimeError("Set a valid OPENAI_API_KEY in .env or Streamlit Secrets")

    structured_llm = llm.with_structured_output(
        TripInfo,
        method="json_schema"
    )

    parsed = invoke_llm_with_rate_limit_retry(structured_llm.invoke,
        f"""
        Extract travel information from the user query.

        Extract these fields:

        1. destination
        - Destination city.

        2. destination_iata
        - Main airport IATA code of the destination.
        - Example: Paris -> CDG

        3. origin
        - Origin city.

        4. origin_iata
        - Main airport IATA code of the origin.
        - Example: New York -> JFK

        5. duration
        - Return ONLY the number of travel days as an integer.
        - Example: "5 days" -> 5

        6. budget
        - Extract the user's stated budget.
        - If no budget is provided, return null.

        7. start_date
        - Convert the travel date to YYYY-MM-DD.
        - If no travel date is provided, return null.

        Do not ask the user for additional information.
        Extract whatever information is available.

        User Query:
        {query}
        """
    )

    return {
        "destination": parsed.destination or "",
        "destination_iata": parsed.destination_iata or "",
        "origin": parsed.origin or "",
        "origin_iata": parsed.origin_iata or "",
        "duration": parsed.duration or 0,
        "budget": parsed.budget or "",
        "start_date": parsed.start_date or "",
        "llm_calls": state.get("llm_calls", 0) + 1
    }


def clarification_agent(state: TravelState):
    missing = []
    if not state.get("destination"):
        missing.append("destination")
    if not state.get("duration"):
        missing.append("trip length")
    details = " and ".join(missing)
    return {
        "clarification": f"To build your itinerary, please share your {details}. You can also include your departure city, travel dates, and budget for more relevant flight and hotel results.",
        "messages": [AIMessage(content="More trip details are needed before planning.")],
    }


def route_after_parser(state: TravelState):
    if not state.get("destination") or not state.get("duration"):
        return "clarification_agent"
    return "flight_agent"


''' ======================================== '''

def flight_agent(state: TravelState):

    origin = state["origin_iata"]
    destination = state["destination_iata"]
    start_date = state["start_date"]

    if not origin or not destination or not start_date:
        flight_result = "Live flight search unavailable: origin airport, destination airport, or travel date is missing."
    else:
        flight_result = search_flights(
            destination=destination,
            origin=origin,
            travel_date=start_date
        )

    # print("\n========== FLIGHT RESULT ==========")
    # print(flight_result)
    
    return {
        'flight_result' : flight_result,
        'messages' : [
            AIMessage(content = "Flight results fetched")
        ],
        # 'llm_calls' : state.get('llm_calls' , 0) + 1
    }












''' ==================================== '''

def hotel_agent(state:TravelState):
    destination = state["destination"]

    if not destination:
        return {
            "hotel_result": "Hotel search unavailable because no destination was provided.",
            "messages": [AIMessage(content="Hotel search skipped: destination missing")],
        }

    hotel_result = tavily_search(
        f"luxury hotels in {destination}; official hotel sites, amenities, published room rates, and reliable hotel details"
    )


    # print("\n========== HOTEL RESULT ==========")
    # print(hotel_result)

    return {
        'hotel_result' : hotel_result,
        'messages' : [
            AIMessage(content = 'Hotels are added')
        ],
        # 'llm_calls' : state.get('llm_calls' , 0) +1
    }








'''====================================='''

def itinerary_agent(state: TravelState):

    prompt = f"""
Original travel request:
{state.get('user_query', '')}
Destination: {state.get('destination') or 'not provided'}
Origin: {state.get('origin') or 'not provided'}
Duration: {state.get('duration') or 'not provided'} days
Budget: {state.get('budget') or 'not provided'}
Travel date: {state.get('start_date') or 'not provided'}

Flight information:
{state.get('flight_result') or 'Unavailable'}
Hotel research evidence:
{state.get('hotel_result') or 'Unavailable'}

Create a personalised day-by-day draft itinerary using the known requirements. Do not ask the traveler to repeat details. Do not invent flight schedules, hotel prices, ratings, or availability. If optional details or live data are missing, say so briefly and continue planning with the information available. Clearly label cost estimates.
"""
    response = invoke_llm_with_rate_limit_retry(llm.invoke, [

        SystemMessage(content = 'You are a professional travel planner ') , 
        HumanMessage(content = prompt)
    
    ])

    return {
        'itinerary' : response.content,
        'messages' : [response],
        'llm_calls': state.get('llm_calls',0)+1
    }










''' ================================== '''

def final_agent(state:TravelState):

    prompt = f'''
        
        You have to plan the whole trip 
        This is user query --> {state['user_query']}

        Parsed trip details: destination={state.get('destination') or 'not provided'}, origin={state.get('origin') or 'not provided'}, duration={state.get('duration') or 'not provided'}, budget={state.get('budget') or 'not provided'}, travel date={state.get('start_date') or 'not provided'}.

        These are the flight details --> {state['flight_result']}

        These are the hotel_result --> {state['hotel_result']}

        This is the itinerary --> {state['itinerary']}
        '''
    
    response = invoke_llm_with_rate_limit_retry(llm.invoke, [
    SystemMessage(
                content="""
        You are a world-class luxury travel consultant.

        RULES:

        1. Never say:
        - Based on the information provided
        - I assume
        - It seems
        - Unfortunately

        2. Write confidently and professionally.

        3. If flight information is missing or unavailable:

        Show:

        ✈ Popular Flight Routes

        and recommend realistic routes using major airports.

        Examples:

        Japan:
        - Delhi (DEL) → Tokyo Haneda (HND)
        - Mumbai (BOM) → Tokyo Narita (NRT)
        - Bangalore (BLR) → Osaka Kansai (KIX)

        London:
        - JFK → LHR
        - DEL → LHR
        - BOM → LHR

        New York:
        - DEL → JFK
        - BOM → JFK

        4. If direct flights are unavailable:

        Suggest alternative routes.

        Example:

        Delhi → Singapore → Tokyo

        Mumbai → Bangkok → Tokyo

        New York → Los Angeles → Tokyo

        5. If hotel information is weak or unavailable:

        Recommend well-known luxury hotels from your knowledge.

        6. Always show only the top 3 hotel recommendations.

        7. Format all money correctly.

        Examples:

        100000 -> $100,000

        1200 -> $1,200

        300 -> $300

        8. Never expose raw search results.
        Use hotel names and facts supported by the hotel evidence, with a source URL for each sourced recommendation. If price, rating, amenities, or availability are not present in the evidence, state that they were not verified; do not invent them. Continue with the known trip details when optional details are missing.

        9. Create a polished travel report using EXACTLY this structure:

        # ✦ Trip Overview

        Destination:
        Origin:
        Duration:
        Budget:
        Travel Date:

        # ✦ Flight Recommendations

        List available flights or suggested routes.

        # ✦ Recommended Hotels

        ### Hotel 1

        Why stay here:

        ### Hotel 2

        Why stay here:

        ### Hotel 3

        Why stay here:

        # ✦ Day-by-Day Itinerary

        ## Day 1

        Morning:
        Afternoon:
        Evening:

        Continue for every day.

        # ✦ Budget Breakdown

        Flights:
        Hotels:
        Food:
        Transportation:
        Activities:
        Miscellaneous:

        Total Estimated Cost:

        # ✦ Travel Tips

        - Tip 1
        - Tip 2
        - Tip 3

        10. If destination is a country instead of a city:

        Recommend the most important cities.

        Example:

        Japan:
        - Tokyo
        - Kyoto
        - Osaka
        - Hakone

        France:
        - Paris
        - Nice
        - Lyon

        11. Output should feel like a premium travel agency report.
        """
            ),
            HumanMessage(content=prompt)
        ])

    final_response = response.content
    if not isinstance(final_response, str) or not final_response.strip():
        raise ValueError("Final agent returned an empty response")

    return {
        "final_response": final_response,
        "messages": [response],
        "llm_calls": state.get("llm_calls", 0) + 1,
    }
