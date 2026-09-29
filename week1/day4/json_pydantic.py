import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key=os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API Error")

client=Groq(api_key=my_api_key)
model="openai/gpt-oss-120b"
role="user"

# structure it
from pydantic import BaseModel
class Ticket(BaseModel):
    name:str
    email:str
    issue:str
schema=Ticket.model_json_schema
response_format={
    "type":"json_object"
}
system_propmt=f"""
Extract the personal information from the ticket.
Return only these three fields: name,email,issue
do not return any other things
strictly based on this schema and give a json output.
{schema}
"""
# System
message_system={
    "role":"system",
    "content":system_propmt
}
text="Hello My name is Pratyush. Yesterday I broke up with my girlfriend sheetal I have an iphone which is not working at all. My address is delhi. My email is abc@gmail.com. My contact number is 82134"
prompt=f"""
This is a customer ticket. Please extract the personal information from this.
{text}
"""
message={
    "role":role,
    "content":prompt
}
messages=[message_system,message]

response=client.chat.completions.create(model=model, messages=messages, response_format=response_format)
answer=response.choices[0].message.content
print(answer)


# isko padhte kaise hai
import json
raw_json=answer
data_file=json.loads(raw_json)
ticket=Ticket(**data_file)


# inko pass kr sakte hai aage!
print(ticket.name)
print(ticket.email)
print(ticket.issue)


