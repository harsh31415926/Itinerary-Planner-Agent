import os 
from typing import TypedDict, Annotated
import operator 

# import psycopg
from langgraph.graph import StateGraph , START , END
# from langgraph.checkpoint.postgres import PostgresSaver

from langchain_core.messages import (AnyMessage , HumanMessage , SystemMessage , AIMessage)

from langchain_groq import ChatGroq

from tools.tavily_tool import tavily_search
from tools.flight_tool import search_flights

from dotenv import load_dotenv
load_dotenv()

from agents import (
    TravelState, 
    flight_agent, 
    parser_agent,
    hotel_agent, 
    itinerary_agent, 
    final_agent
)


# DATABASE_URL = os.getenv('DATABASE_URL')

# Grapgh Compilation

graph = StateGraph(TravelState)

graph.add_node('parser_agent' , parser_agent)
graph.add_node('flight_agent' , flight_agent)
graph.add_node('hotel_agent' , hotel_agent)
graph.add_node('itinerary_agent' , itinerary_agent)
graph.add_node('final_agent' , final_agent)

graph.add_edge(START , 'parser_agent')
graph.add_edge('parser_agent' , 'flight_agent')
graph.add_edge('flight_agent' , 'hotel_agent')
graph.add_edge('hotel_agent' , 'itinerary_agent')
graph.add_edge('itinerary_agent' , 'final_agent')
graph.add_edge('final_agent' , END)

# print(DATABASE_URL)

# print("DATABASE_URL =", repr(DATABASE_URL))

# Database Connection POSTGRES
# __conn = psycopg.connect(
#     DATABASE_URL,
#     autocommit=True
# )

# checkpointer = PostgresSaver(__conn)
# checkpointer.setup()


app = graph.compile()

# print(app.get_graph().draw_mermaid())    # It WILL print the graph of node


if __name__ == '__main__':

    config = {
        'configurable': {
            'thread_id' : 'Harsh'
        }
    }

    user_input = input('Enter your Query : ')



    result = app.invoke(
        {
            "user_query": user_input,

            "destination": "",
            "origin": "",
            "budget": "",
            "duration": 0,
            "start_date": "",

            "flight_result": "",
            "hotel_result": "",
            "itinerary": "",

            "messages": [
                HumanMessage(content=user_input)
            ],

            "llm_calls": 0
        },
        config = config
    )

    # print("\n========== FINAL ITINERARY ==========")
    # print(result['itinerary'])


    # print("\nDEBUG STATE\n")
    # print(result['flight'])

    # print('\nFinal Response\n')

    # for msg in result['messages']:
    #     print(msg.content)
    #     print(result["flight_result"])
    #     print(result["hotel_result"])
    