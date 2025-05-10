import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv

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