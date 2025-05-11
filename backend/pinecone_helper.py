import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from models import SearchQuery
from similarity_helper import get_relevant_authors, get_relevant_journals

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")

# pinecone setup
pc = Pinecone(api_key=PINECONE_API_KEY)


def pc_create_index(name: str, dimension: int, metric: str, cloud: str, region: str):
    indexes = pc.list_indexes()
    names = [index["name"] for index in indexes]
    if name not in names:
        pc.create_index(
            name=name,
            dimension=dimension,
            metric=metric,
            spec=ServerlessSpec(
                cloud=cloud,
                region=region
            )
        )
    return pc.Index(name)


def pc_get_index(name: str):
    indexes = pc.list_indexes()
    names = [index["name"] for index in indexes]
    if name not in names:
        return None
    return pc.Index(name)


def upsert_document_vectors(name: str, vectors: list):
    index = pc_get_index(name)
    index.upsert(vectors)


def upsert_document_vectors_by_batches(name: str, vectors: list, batch_size: int):
    for i in range(0, len(vectors), batch_size):
        batch = vectors[i:i + batch_size]
        try:
            upsert_document_vectors(name, batch)
        except Exception as e:
            print(f"[ERROR] Failed to upsert batch: {e} (batch size: {len(batch)})")


def get_document_by_id(name: str, id: str):
    index = pc_get_index(name)
    response = index.fetch(ids=[id])
    vector_data = response.vectors.get(id)
    return vector_data


def delete_document_by_ids(name: str, uids: list):
    index = pc_get_index(name)
    index.delete(ids=uids)


def delete_all_documents(name: str):
    index = pc_get_index(name)
    index.delete(delete_all=True)


def query_vectors(name: str, vector: list[float], top_k=5, metadata_filter=None, include_metadata=True):
    index = pc_get_index(name)
    return index.query(
        vector=vector,
        top_k=top_k,
        filter=metadata_filter,
        include_metadata=include_metadata
    )


def build_metadata_filter(query_params: SearchQuery):
    metadata_filter = {}

    # Author filter: supports OR across authors (e.g., match any author)
    if query_params.authors:
        user_entered_authors = [a.strip() for a in query_params.authors.split(",") if a.strip()]
        authors = get_relevant_authors(user_entered_authors, "authors.csv")
        if authors:
            metadata_filter["authors"] = {"$in": authors}

    # Journal filter: supports OR across journals
    if query_params.journal:
        user_entered_journals = [j.strip().lower() for j in query_params.journal.split(",") if j.strip()]
        journals = get_relevant_journals(user_entered_journals, "journals.csv")
        if journals:
            metadata_filter["journal"] = {"$in": journals}

    # Data filters
    date_conditions = []

    if query_params.start_year is not None:
        start_or = [{"published_year": {"$gt": query_params.start_year}}]
        if query_params.start_month is not None:
            start_or.append({
                "$and": [
                    {"published_year": query_params.start_year},
                    {"published_month": {"$gte": query_params.start_month}}
                ]
            })
        else:
            start_or.append({"published_year": query_params.start_year})

        date_conditions.append({"$or": start_or})

    if query_params.end_year is not None:
        end_or = [{"published_year": {"$lt": query_params.end_year}}]
        if query_params.end_month is not None:
            end_or.append({
                "$and": [
                    {"published_year": query_params.end_year},
                    {"published_month": {"$lte": query_params.end_month}}
                ]
            })
        else:
            end_or.append({"published_year": query_params.end_year})

        date_conditions.append({"$or": end_or})

    if date_conditions:
        metadata_filter["$and"] = date_conditions

    return metadata_filter or None
