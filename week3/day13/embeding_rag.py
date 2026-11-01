import os
from groq import Groq
from dotenv import load_dotenv
import numpy as np
from sentence_transformers import SentenceTransformer

load_dotenv()

# my_api_key = os.getenv("GROQ_API_KEY")

# if not my_api_key:
#     raise ValueError("GROQ_API_KEY environment variable is not set.")

# client = Groq(api_key=my_api_key)
# model="openai/gpt-oss-120b"

embeddingModel = SentenceTransformer('all-MiniLM-L6-v2')# sentance vector will be 384
# text="Machine learning is fun"
# result=embeddingModel.encode(text) 
# print(result[:10])

def cosing_similarity(vec1, vec2):
    return np.dot(vec1, vec2)/(np.linalg.norm(vec1)*np.linalg.norm(vec2))

t1="There are 24 paid leave"
l2="I have 24 vactions"
print(cosing_similarity(embeddingModel.encode(t1), embeddingModel.encode(l2)))




