from openai import OpenAI
from google import genai
import os
from dotenv import load_dotenv, dotenv_values 
# loading variables from .env file
load_dotenv() 

# accessing and printing value
GEMINI_KEY = os.getenv("GEMINI_KEY")

with open("stats_no_block.xml", 'r') as file, open("stats_block.xml", 'r') as file2:
    control_buffer = file.read()
    blocked_buffer = file2.read()

client = genai.Client(api_key = GEMINI_KEY)
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

# client = OpenAI(
#     base_url="https://generativelanguage.googleapis.com/v1beta/openai/",
#     # base_url="https://api.deepseek.com/v1",
#     api_key=GEMINI_KEY
#     )
# # print(control_buffer)

# differences = client.chat.completions.create(
#     model="gemini-2.5-flash",
#     messages=[
#         {"role":"user", "content": f"""
#         These two XML files represent traffic data simulations before and after blocking a lane temporarily. Compare both data outputs and explain what the aggregate,
#         hollistic impact was on traffic when adding the block. This should include delays, unexpected braking, and length of congestion.

#         without blocks:

#         {control_buffer}

#         with block:
        
#         {blocked_buffer}

#     """}
#     ]
# )

# print(differences.choices[0].message.content)
