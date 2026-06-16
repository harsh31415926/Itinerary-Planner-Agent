import os 
from typing import TypedDict, Annotated
from pydantic import BaseModel
import operator 
import json

import psycopg
from langgraph.graph import StateGraph , START , END
from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (AnyMessage , HumanMessage , SystemMessage , AIMessage)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()


GROQ_API_KEY = os.getenv("GROQ_API_KEY")

llm = ChatGroq(
    model = 'llama-3.3-70b-versatile',
    api_key=GROQ_API_KEY
)

class TripInfo(BaseModel):
    destination: str | None = None
    destination_iata: str | None = None
    origin: str | None = None
    origin_iata : str | None = None
    duration: str | None = None
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

    structured_llm = llm.with_structured_output(TripInfo)

    parsed = structured_llm.invoke(
        f"""
        Extract:
        - destination city
        - destination airport IATA code
        - origin city
        - origin airport IATA code
        - duration
        - budget
        - travel date

        Convert dates to YYYY-MM-DD format.

        Example:

        destination = London
        destination_iata = LHR

        origin = New York
        origin_iata = JFK

        User Query:
        {query}
        """
    )

    print("\n===== PARSED DATA =====")

    print("Destination:", parsed.destination)
    print("Origin:", parsed.origin)
    print("Duration:", parsed.duration)
    print("Budget:", parsed.budget)
    print("Date:", parsed.start_date)

    return {
        "destination": parsed.destination or "",
        "destination_iata":parsed.destination_iata or "",
        "origin": parsed.origin or "",
        "origin_iata" : parsed.origin_iata or "",
        "duration": int(parsed.duration.split()[0]) if parsed.duration else 0,
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

    print("\n========== FLIGHT RESULT ==========")
    print(flight_result)
    
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


    print("\n========== HOTEL RESULT ==========")
    print(hotel_result)

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
        SystemMessage(content ='''You are an expert travel planner. Your job is to create a complete, accurate, and easy-to-understand travel itinerary using the flight details, hotel information, and activity recommendations provided by the user. Generate a well-organized travel plan that includes transportation, accommodation, and daily activities. Present the itinerary in a natural and traveler-friendly manner using clear paragraphs. Organize activities in a logical sequence, group nearby attractions together when possible, and optimize the schedule for convenience and minimal travel time.Include important details such as flight schedules, hotel check-in and check-out information, recommended activities, travel tips, and any useful notes that may enhance the travel experience. If some information is missing, make reasonable assumptions and clearly indicate them.Your response should be practical, concise, engaging, and focused on helping the traveler enjoy a smooth and memorable trip.
'''), 
        HumanMessage(content = prompt)
    ])

    return {
    "itinerary": response.content,
    "messages": [response],
    "llm_calls": state.get("llm_calls", 0) + 1
}
