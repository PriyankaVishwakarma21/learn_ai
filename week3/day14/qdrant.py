# ============================================================
# PART 1 — IMPORTS AND ENVIRONMENT
# ============================================================

import os
from groq import Groq
from dotenv import load_dotenv
from qdrant_client import QdrantClient
from qdrant_client.http.models import VectorParams, Distance, PointStruct
from sentence_transformers import SentenceTransformer

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

# ============================================================
# PART 2 — CONNECT TO QDRANT
# ============================================================

#create client for Qdrant
client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY)

print("Qdrant client initialized successfully.")

# ============================================================
# PART 3 — CREATE QDRANT COLLECTION
# ============================================================

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

print(f"Collection '{COLLECTION_NAME}' created successfully.")
print(f"Embedding size: {EMBEDDING_SIZE}, Distance metric: COSINE")

# ============================================================
# PART 4 — LOAD OUR KNOWLEDGE
# ============================================================


# load our knowledge base
with open("knowledge.txt", "r", encoding="utf-8") as f:
    documents = [
        line.strip()
        for line in f
        if line.strip()
    ]
# ["line 1 ", "line2", "line3"....]
print(f"Loaded {len(documents)} documents")


# ============================================================
# PART 5 — CREATE EMBEDDINGS
# ==========================================================

embeddingModel = SentenceTransformer('all-MiniLM-L6-v2')# sentance vector will be 384

embeddedDocuments = embeddingModel.encode(documents)

# ============================================================
# PART 6 — CREATE QDRANT POINTS
# ============================================================

#create qdrant points
points=[]

for i, doc in enumerate(embeddedDocuments):
    point = PointStruct(
        id=i,
        vector=doc.tolist(),
        payload={"text": documents[i]}
    )
    points.append(point)


# ============================================================
# PART 7 — UPLOAD TO QDRANT
# ============================================================

#upsert points into qdrant collection
client.upsert(
    collection_name=COLLECTION_NAME,
    points=points
)

print(f"Uploaded {len(points)} documents to Qdrant!")

# ============================================================
# PART 8 — SEARCH QDRANT
# ============================================================

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


# ============================================================
# PART 9 — TEST SEARCH
# ============================================================

results = search("How many paid leaves do I have?",3)

print("\nSearch results:")

for result in results:
    print(f"Score: {result.score:.3f}")
    print(result.payload["text"])
    print()


# ============================================================
# PART 10 — CONNECT TO GROQ
# ============================================================

groq_client = Groq(api_key=GROQ_API_KEY)
groq_model = "openai/gpt-oss-120b"

# ============================================================
# PART 11 — ASK THE LLM
# ============================================================

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


# ============================================================
# PART 12 — COMPLETE RAG PIPELINE
# ============================================================

question = "How many vacation days do I get?"

results = search(question, top_k=3)


# Extract text from the search results
context = "\n".join(
    result.payload["text"]
    for result in results
)


answer = ask_llm(question, context)


print("\nFinal Answer:")
print(answer)