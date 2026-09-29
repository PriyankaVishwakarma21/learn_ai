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
prompt1="Hi"
prompt2="Explain time travel in details"
prompt3="write 1000 word easy on machine learning"
prompt="Suggest me food company name"
prompts=[prompt1,prompt2,prompt3]
for prompt in prompts:
    message={
    "role":role,
    "content":prompt
    }
    messages=[message]
    response=client.chat.completions.create(model=model, messages=messages, max_tokens=50)
    usage=response.usage
    print(f"Prompt: {prompt} -->your tokens: {usage.prompt_tokens} completion_tokens: {usage.completion_tokens} total tokens: {usage.total_tokens}  Finish Reason: {response.choices[0].finish_reason}")




# Prompt: Hi -->your tokens: 72 completion_tokens: 41 total tokens: 113  Finish Reason: stop
# Prompt: Explain time travel in details -->your tokens: 76 completion_tokens: 50 total tokens: 126  Finish Reason: length
# Prompt: write 1000 word easy on machine learning -->your tokens: 80 completion_tokens: 50 total tokens: 130  Finish Reason: length

# Finish Reason: stop this means stoped
# Finish Reason: length this means stopped forcefully because we have set the max_tokens