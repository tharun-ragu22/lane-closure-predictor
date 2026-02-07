import sys
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


print(sys.argv[1])
user_text = sys.argv[1]
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
            {"role":"user", "content": f"Give me a coordinate on the 401 in the location specified here: {user_text}"}
        ],
    response_format=LatLng
)

# response = client.responses.create(
#     model="gpt-5-nano",
#     input="Give me a coordinate just west of Neilson Rd on Hwy 401"
# )


res : LatLng = response.choices[0].message.parsed
print('result latlng:', res)

closest_edge = get_closest_edge(res.lat, res.lng, EDGE_LOCATIONS_FILE)

control_file = run_simulation()

blocked_file = run_simulation(closest_edge)

with open(control_file, 'r') as file, open(blocked_file, 'r') as file2:
    control_buffer = file.read()
    blocked_buffer = file2.read()

client = genai.Client(api_key = GEMINI_KEY)

import json
import os
from google.cloud import storage

def save_results_to_gcs(data_dict):
    # Get the unique execution ID provided by Cloud Run
    execution_id = os.environ.get("CLOUD_RUN_EXECUTION", "local_test")
    bucket_name = os.environ.get("RESULTS_BUCKET")
    
    # Initialize the GCS client
    client = storage.Client()
    bucket = client.bucket(bucket_name)
    
    # Create a blob (file) named after the execution ID
    blob = bucket.blob(f"results/sim_{execution_id}.json")
    
    # Upload the data as a JSON string
    blob.upload_from_string(
        data=json.dumps(data_dict),
        content_type='application/json'
    )
    print(f"Logged results to gs://{bucket_name}/{blob.name}")


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
save_results_to_gcs({"status": "complete", "analysis": response.text})

print(response.text)