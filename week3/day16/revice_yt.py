import os
import json
from groq import Groq
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer
from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct,PayloadSchemaType, Filter, FieldCondition, MatchValue

load_dotenv()

QDRANT_API_KEY = os.getenv("QDRANT_API_KEY")
QDRANT_URL = os.getenv("QDRANT_URL")
GROQ_API_KEY = os.getenv("GROQ_API_KEY")

client = QdrantClient(url=QDRANT_URL, api_key=QDRANT_API_KEY, timeout=60)

COLLECTION_NAME = "revice_yt"
EMBEDDING_SIZE = 384

if client.collection_exists(COLLECTION_NAME):
    print(f"Collection {COLLECTION_NAME} already exists.")
    client.delete_collection(COLLECTION_NAME)

client.create_collection(collection_name=COLLECTION_NAME, vectors_config=VectorParams(size=EMBEDDING_SIZE,distance=Distance.COSINE))

print(f"Vector DB connection successfully")

client.create_payload_index(collection_name=COLLECTION_NAME, field_name="title",field_schema=PayloadSchemaType.KEYWORD)

print(f"added payload index to collection")


# load all the json files from folder transcribe
folder_path = 'transcribe'
json_files = [f for f in os.listdir(folder_path) if f.endswith('.json')]

all_data = []
for file_name in json_files:
    file_path = os.path.join(folder_path, file_name)
    with open(file_path, 'r') as file:
        data = json.load(file)
        all_data.append(data)

print(f"Loaded {len(all_data)} JSON files from {folder_path}")

# embedding all_data
embeddingModel = SentenceTransformer('all-MiniLM-L6-v2')

print(" embedding started")

texts = [data.get("text") or data.get("full_text", "") for data in all_data]

embeddedDocuments = embeddingModel.encode(texts,batch_size=32,show_progress_bar=True)

print(f"Embedding len: {len(embeddedDocuments)}")
print(f"Embedded Doc size: {len(embeddedDocuments[0])}")

# create points

points = []

for i in range(len(all_data)):
  point = PointStruct(
    id=i+1,
    vector=embeddedDocuments[i].tolist(),
    payload={
      "title": all_data[i].get("title", ""),
      "channel": all_data[i].get("channel", "Gaurav Sen"),
      "text": all_data[i].get("text") or all_data[i].get("full_text", ""),
      "url": all_data[i].get("url", ""),
      "timestamp": all_data[i].get("timestamp", "00:00")
    }
  )
  points.append(point)


# upsert point into vector db
client.upsert(collection_name=COLLECTION_NAME, points=points)

print(f"upserted {len(points)} points successfully")

# search function
def search(query,top_k=5):
    query_embedding = embeddingModel.encode(query).tolist()
    hits = client.query_points(
        collection_name=COLLECTION_NAME,
        query=query_embedding,
        limit=top_k,
        with_payload=True
    ).points
    return hits


# search with filter
def search_with_filter(query,query_filter=None,top_k=3):
  query_emb = embeddingModel.encode(query).tolist()
  hits = client.query_points(
      collection_name=COLLECTION_NAME,
      query=query_emb,
      limit=top_k,
      with_payload=True,
      query_filter=query_filter
  ).points
  return hits


# Create text/title filter example (optional)
title_filter = Filter(
  must=[
    FieldCondition(
      key="title",
      match=MatchValue(
        value="Working Of A System | System Design Course Ep 2"
      )
    )
  ]
)

# Create groq client

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
question = "How system works"

# Search with filter or without filter (query_filter=None searches all videos)
results = search_with_filter(question, query_filter=None, top_k=2)


# Extract text from the search results (truncated to fit model token limits)
context = "\n\n".join(
    f"Video: {result.payload.get('title', '')}\nTranscript:\n{result.payload.get('text', '')[:3500]}"
    for result in results
)

answer = ask_llm(question, context)


print("\nFinal Answer:")
print(answer)






# url = "https://www.youtube.com/watch?v=RNa0Lx4nu80&list=PLCy4-Mb2upaQ"
# # Fetch transcripts (both in memory and saved to transcribe/)
# transcripts = download_youtube_transcript(url, output_dir="transcribe")
# for item in transcripts:
#     print(f"Video: {item['title']}")
#     print(f"Full text length: {len(item['full_text'])} characters")
