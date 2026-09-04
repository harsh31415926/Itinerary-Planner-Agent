import os 
from typing import TypedDict, Annotated
from pydantic import BaseModel
import operator 
import json

# import psycopg
from langgraph.graph import StateGraph , START , END
# from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (AnyMessage , HumanMessage , SystemMessage , AIMessage)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model="openai/gpt-oss-20b",
    api_key=GROQ_API_KEY,
    temperature=0
)

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
    llm_calls: int







''' ========================================== '''



def parser_agent(state: TravelState):

    query = state["user_query"]

    structured_llm = llm.with_structured_output(
        TripInfo,
        method="json_schema"
    )

    parsed = structured_llm.invoke(
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


''' ======================================== '''

def flight_agent(state: TravelState):

    origin = state["origin_iata"]
    destination = state["destination_iata"]
    start_date = state["start_date"]

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

    hotel_result = tavily_search(
        f"top luxury hotels in {destination} with ratings and prices, don't give me links, just tell me the name of the hotel and the ratings of that "
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
Destination:
{state['destination']}

Origin:
{state['origin']}

Duration:
{state['duration']} days

Budget:
{state['budget']}

Travel Date:
{state['start_date']}

Flight Information:
{state['flight_result']}

Hotel Information:
{state['hotel_result']}
"""
    response = llm.invoke([

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

        These are the flight details --> {state['flight_result']}

        These are the hotel_result --> {state['hotel_result']}

        This is the itinerary --> {state['itinerary']}
        '''
    
    response = llm.invoke([
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

    return {
    "itinerary": response.content,
    "messages": [response],
    "llm_calls": state.get("llm_calls", 0) + 1
}
