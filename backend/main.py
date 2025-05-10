from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from create_embeddings import get_embedding
from pinecone_helper import query_vectors
import os
from datetime import datetime

load_dotenv()
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

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


def format_date(iso_date: str):
    try:
        dt = datetime.strptime(iso_date, "%Y-%m-%dT%H:%M:%SZ")
        return dt.strftime("%Y-%m-%d")
    except Exception:
        return None


@app.get("/search/")
def search(query: str):
    query_embedding = get_embedding(query)
    print("got embedding")
    docs = query_vectors(PINECONE_INDEX, query_embedding)
    print("got docs")
    matches = docs["matches"]
    print(f"got matches of length {len(matches)}")

    return {
        "papers": [
            {
                "title": m["metadata"].get("title"),
                "authors": m["metadata"].get("authors", []),
                "date": format_date(m["metadata"].get("published_date")),
                "abstract": m["metadata"].get("abstract"),
                "score": m["score"]
            }
            for m in matches
        ]
    }


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
