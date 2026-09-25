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
prompt="Suggest me food company name"
# System
message_system={
    "role":"system",
    "content":"You are brand manager who suggest name for my food company. name should be in oe word. suggest me only one name"
}
message={
    "role":role,
    "content":prompt
}
messages=[message_system,message]
# Temprature is by default 0 meaning safe, range b/w 0,2
response=client.chat.completions.create(model=model, messages=messages, temperature=1)
# print(response)

print("##########################")
print(response.choices[0].message.content)

