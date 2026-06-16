import os 
import requests 
from dotenv import load_dotenv

load_dotenv()

API_KEY = os.getenv("AVIATION_STACK_API_KEY")


def search_flights(origin: str, destination: str , travel_date:str) -> str:
    url = "http://api.aviationstack.com/v1/flights"

    params = {
        "access_key": API_KEY,
        'dep_iata' : origin,
        "arr_iata": destination,  
        'travel_date' : travel_date,
        "limit": 7
    }

    response = requests.get(url, params = params)
    # print(response)

    data = response.json()
    # print(data)

    flights = []

    if "data" in data :
        
        for flight in data['data'][:params['limit']]:

            airline = flight.get('airline' ,{}).get('name' , 'unknown')
            arrival = flight.get('arrival' ,{}).get('airport' , 'unknown')
            departure = flight.get('departure' ,{}).get('airport' , 'unknown') 
            status = flight.get('flight_status' , 'unknown')

            # print(f'{airline} \n {arrival} \n {departure} \n {status} \n\n')
            flights.append(
                f"""Airline : {airline} | Departure : {departure} | Arrival : {arrival} | Status : {status}"""
            )
        
    return "\n".join(flights) if flights else "No flights are there for the given destination"


# res = search_flights('JFK' , 'DCA')
# print(res)