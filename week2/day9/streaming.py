import os
from dotenv import load_dotenv
from groq import Groq

load_dotenv()
my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("API Error")

client = Groq(api_key=my_api_key)
model = "openai/gpt-oss-120b"

prompt="Explain how internet works"
messages=[{"role":"user","content":prompt}]
# response=client.chat.completions.create(
#     model=model,
#     messages=messages) #bydefault streaming is set to False
# answer=response.choices[0].message.content
# print("Answer:",answer)


stream_response=client.chat.completions.create(model=model,messages=messages,stream=True) #bydefault streaming is set to False
print("Streaming Answer:")

for chunk in stream_response:
    content=chunk.choices[0].delta.content
    if content:
        print(content,end="",flush=True)# flush=True is used to force the output to be printed immediately without buffering