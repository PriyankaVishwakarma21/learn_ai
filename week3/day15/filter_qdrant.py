
import os
import json
from groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue, MatchAny, PayloadSchemaType
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

print("Qdrant client initialized successfully.")

COLLECTION_NAME="knowledge_base"
EMBEDDING_SIZE=384

# if collection already exists, delete it
if client.collection_exists(COLLECTION_NAME):
    print(f"Collection '{COLLECTION_NAME}' already exists.")
    client.delete_collection(COLLECTION_NAME)

#create collection with embedding size and distance metric
client.create_collection(
    collection_name=COLLECTION_NAME,
    vectors_config=VectorParams(size=EMBEDDING_SIZE, distance=Distance.COSINE)
)

# Create index for filtering
client.create_payload_index(
    collection_name=COLLECTION_NAME,
    field_name="category",
    field_schema=PayloadSchemaType.KEYWORD
)

print(f"Collection '{COLLECTION_NAME}' created successfully.")
print(f"Embedding size: {EMBEDDING_SIZE}, Distance metric: COSINE")

#load knowledge.json

with open("knowledge.json","r",encoding="utf-8") as f:
    documents=json.load(f)

print(f"Documents: {documents}")
print(f"Document length :{len(documents)}")

# embedding docs
embeddingModel = SentenceTransformer('all-MiniLM-L6-v2')

# we have to embed text only

texts = [doc["text"] for doc in documents]

embeddedDocuments = embeddingModel.encode(texts)

print(f"Embeddig len: {len(embeddedDocuments)}")
print(f"Embedded Doc size: {len(embeddedDocuments[0])}")

# create points

points = []

for i in range(len(documents)):
    point=PointStruct(
        id=i+1,
        vector=embeddedDocuments[i].tolist(),
        payload=documents[i]
    )
    points.append(point)

# upsert points in collection
client.upsert(collection_name=COLLECTION_NAME,points=points)

print("upserted successfully")
print(f"Uploaded points len: {len(points)}")

# search function
def search(query, top_k=3):

    # Convert the question into an embedding
    query_vector = embeddingModel.encode(query).tolist()

    # Search Qdrant for similar vectors
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_vector,
        limit=top_k,
        with_payload=True,
    ).points

    return results

# search with filter
def search_with_filter(query, query_filter=None, top_k=3):
    #embed query
    query_embed = embeddingModel.encode(query).tolist()
    results = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embed,
        limit=top_k,
        with_payload=True,
        query_filter=query_filter
    ).points
    return results

#create filter
reimbursement_filter=Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="reimbursement")
        )
    ]
)

leave_filter = Filter(
    must=[
        FieldCondition(
            key="category",
            match=MatchValue(value="leave")
        )
    ]
)

groq_client = Groq(api_key=GROQ_API_KEY)
groq_model = "openai/gpt-oss-120b"

# aks_llm
def ask_llm(question, context):

    prompt = f"""
Answer the question using only the information provided below.

Context:
{context}

Question:
{question}

If the answer is not present in the context, say:
"I don't know based on the provided information."
"""

    response = groq_client.chat.completions.create(
        model=groq_model,
        messages=[
            {
                "role": "user",
                "content": prompt
            }
        ]
    )

    return response.choices[0].message.content

# ask question 

question="How many vacation days do I get?"

results = search_with_filter(question,leave_filter,3)

# Extract text from the search results
context = "\n".join(
    result.payload["text"]
    for result in results
)

answer = ask_llm(question, context)


print("\nFinal Answer:")
print(answer)