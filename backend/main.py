from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pinecone_helper import query_vectors, build_metadata_filter, get_document_by_id
from openai_helper import query_llm, get_embedding
import os
from datetime import datetime
from fastapi import Depends
from models import SearchQuery
import requests
import fitz
import re

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


def extract_arxiv_id(url: str) -> str | None:
    patterns = [
        r'arxiv\.org/abs/([0-9]+\.[0-9]+)',       # abs page
        r'arxiv\.org/pdf/([0-9]+\.[0-9]+)',       # pdf link
        r'arxiv\.org/abs/([a-z\-]+/[0-9]+)',      # old style IDs (e.g., hep-th/9901001)
        r'arxiv\.org/pdf/([a-z\-]+/[0-9]+)'       # old style PDF links
    ]

    for pattern in patterns:
        match = re.search(pattern, url)
        if match:
            return match.group(1)

    return None


@app.get("/search/")
def search(query_params: SearchQuery = Depends()):
    query_embedding = get_embedding(query_params.query)
    print("got embedding")

    metadata_filter = build_metadata_filter(query_params)

    docs = query_vectors(PINECONE_INDEX, query_embedding, 10, metadata_filter)
    print("got docs")
    matches = docs["matches"]
    print(f"got matches of length {len(matches)}")

    return {
        "papers": [
            {
                "id": m.get("id"),
                "title": m["metadata"].get("title"),
                "authors": m["metadata"].get("authors", []),
                "date": format_date(m["metadata"].get("published_date")),
                "abstract": m["metadata"].get("abstract"),
                "score": m["score"],
                "link": m["metadata"].get("link"),
                "journal": m["metadata"].get("journal")
            }
            for m in matches
        ]
    }


@app.get("/details")
def details(paper_id: str):
    paper = get_document_by_id(PINECONE_INDEX, paper_id)
    metadata = paper.metadata
    link = metadata.get("link")

    # retrieve pdf + convert to text
    arxiv_id = extract_arxiv_id(link)
    pdf_url = f"https://arxiv.org/pdf/{arxiv_id}.pdf"
    response = requests.get(pdf_url)
    with open("paper.pdf", "wb") as f:
        f.write(response.content)

    doc = fitz.open("paper.pdf")
    paper_text = ""
    for page in doc:
        paper_text += page.get_text()

    # get summary
    prompt = f"""
    Summarize the following research paper. 
    Be high level, use no more than 8 sentences. 
    The summary must be in paragraph form. 
    
    Research paper: {paper_text}"""
    llm_summary = query_llm(prompt)

    # get similar docs:
    embedding = paper.values
    relevant_docs = query_vectors(PINECONE_INDEX, embedding)
    matches = relevant_docs["matches"]
    formatted_docs = [
            {
                "id": m.get("id"),
                "title": m["metadata"].get("title"),
                "authors": m["metadata"].get("authors", []),
                "date": format_date(m["metadata"].get("published_date")),
                "abstract": m["metadata"].get("abstract"),
                "score": m["score"],
                "link": m["metadata"].get("link"),
                "journal": m["metadata"].get("journal")
            }
            for m in matches
    ]

    return {
        "title": metadata.get("title"),
        "authors": metadata.get("authors", []),
        "date": format_date(metadata.get("published_date")),
        "abstract": metadata.get("abstract"),
        "link": link,
        "journal": metadata.get("journal"),
        "llm_summary": llm_summary,
        "relevant_docs": formatted_docs
    }


# Root endpoint
@app.get("/")
def read_root():
    return {"message": "Welcome to FastAPI!"}
