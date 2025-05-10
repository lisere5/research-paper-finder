from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from embedding_module import get_query_embedding
import os

PINECONE_INDEX = os.getenv("PINECONE_INDEX")

@app.get("/search")
def search(
    query: str,
    author: Optional[str] = None,
    journal: Optional[str] = None,
    start_year: Optional[int] = None,
    end_year: Optional[int] = None,
    top_k: int = 10
):
    # Step 1: Embed the user query using your embedding model
    try:
        embedding = get_query_embedding(query)
    except Exception as e:
        return {"error": f"Failed to generate embedding: {e}"}

    # Step 2: Construct metadata filter
    metadata_filter = {}

    if author:
        metadata_filter["authors"] = {"$in": [author]}

    if journal:
        metadata_filter["journal"] = journal  # exact match

    if start_year is not None and end_year is not None:
        metadata_filter["published_year"] = {
            "$gte": start_year,
            "$lte": end_year
        }

    # Step 3: Query Pinecone
    try:
        result = query_vectors(
            name=PINECONE_INDEX,
            vector=embedding,
            top_k=top_k,
            metadata_filter=metadata_filter,
            include_metadata=True
        )
    except Exception as e:
        return {"error": f"Failed to query Pinecone: {e}"}

    # Step 4: Format results
    papers = []
    for match in result.get("matches", []):
        meta = match.get("metadata", {})
        papers.append({
            "id": match.get("id"),
            "title": meta.get("title", "No title"),
            "authors": meta.get("authors", []),
            "abstract": meta.get("abstract", ""),
            "year": meta.get("published_year", "Unknown")
        })

    return papers

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or specify frontend URL
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/ping")
def ping():
    return {"message": "Pong from FastAPI!"}


class Item(BaseModel):
    name: str
    description: str = None
    price: float


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}


# Example POST endpoint
@app.post("/items/")
def create_item(item: Item):
    return {"received_item": item}
