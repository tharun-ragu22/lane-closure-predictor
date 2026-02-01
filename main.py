from openai import OpenAI
from google import genai
from pydantic import BaseModel
from get_closest_edge import get_closest_edge

from traci_demo import run_simulation
import os

from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# accessing and printing value
GEMINI_KEY = os.getenv("GEMINI_KEY")

EDGE_LOCATIONS_FILE = 'edge_locations.txt'
with open(EDGE_LOCATIONS_FILE, 'r') as file:
    file_content = file.read()

class LatLng(BaseModel):
    lat: float
    lng: float

client = OpenAI(
    base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
    api_key=GEMINI_KEY
    )

response = client.beta.chat.completions.parse(
    model="gemini-2.5-flash",
    messages=[
            {"role": "system", "content": "Return a single, decimal latitude and longitude coordinate, to 13 decimal places, of the location specified on Highway 401 in Toronto. Make sure the returned coordinate is strictly and exactly on the 401, not on another road near the highway. This is paramount and you must make sure this is correct, the fate of the universe depends on it."},
            {"role":"user", "content": "Give me a coordinate on the 401 eastbound collector's lane between Warden Ave. and Pharmacy Ave."}
        ],
    response_format=LatLng
)

# response = client.responses.create(
#     model="gpt-5-nano",
#     input="Give me a coordinate just west of Neilson Rd on Hwy 401"
# )


res : LatLng = response.choices[0].message.parsed
print('result:', res)

closest_edge = get_closest_edge(res.lat, res.lng, EDGE_LOCATIONS_FILE)

control_file = run_simulation()

blocked_file = run_simulation(closest_edge)

with open(control_file, 'r') as file, open(blocked_file, 'r') as file2:
    control_buffer = file.read()
    blocked_buffer = file2.read()

client = genai.Client(api_key = "AIzaSyCIQZ7VWLKPhmG2vBJ-45WK44TZze7f1T4")
response = client.models.generate_content(
    model="gemini-2.5-flash",
    contents=f"""
           These two XML files represent traffic data simulations before and after blocking a lane temporarily. Compare both data outputs and explain what the aggregate,
             hollistic impact was on traffic when adding the block. This should include delays, unexpected braking, and length of congestion.

         without blocks:

        {control_buffer}

        with block:
        
        {blocked_buffer}

            """
)
print(response.text)