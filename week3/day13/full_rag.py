import os
from groq import Groq
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer 
load_dotenv()

embeddingModel = SentenceTransformer('all-MiniLM-L6-v2')# sentance vector will be 384

my_api_key = os.getenv("GROQ_API_KEY")

if not my_api_key:
    raise ValueError("GROQ_API_KEY environment variable is not set.")   

client= Groq(api_key=my_api_key)
groqModel="openai/gpt-oss-120b"

#knowledge base
documents = [
    "Employees receive 24 days of paid leave per year.",
   
    "Employees work from the office on Tuesday, Wednesday and Thursday. "
    "Monday and Friday are optional work-from-home days.",
   
    "Employees receive Rs 3000 per month for gym reimbursement.",
   
    "Employees can claim Rs 2000 per month for home internet.",
   
    "Employees have a 90 day notice period."
]

documents_embeddings = embeddingModel.encode(documents)

def cosing_similarity(vec1, vec2):
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))

# Give highest score document as context to LLM
def retrive(query_embedding):
    scores=[]
    for i, doc_embedding in enumerate(documents_embeddings):
        score = cosing_similarity(query_embedding, doc_embedding)
        scores.append((score, documents[i]))
    scores.sort(reverse=True)#it store the highest score at the top
    return scores[0]


def ask_llm(question,context):

    sys_prompt=f"""answer in one line only. Answer only based on this context. do not hallucinate. Context: {context}"""
    system_message={
        "role": "system",
        "content": sys_prompt

    }
    message={
        "role": "user",
        "content": question
    }
    messages=[system_message, message]
    response=client.chat.completions.create(model=groqModel, messages=messages)
    answer=response.choices[0].message.content
    return answer


query = "I love pizza."
query_embedding = embeddingModel.encode(query)
score,context=retrive(query_embedding)
print(f"Score: {score}", f"Context: {context}")
answer=ask_llm(query,context)
print(f"Question: {query}")
print(f"Answer: {answer}")