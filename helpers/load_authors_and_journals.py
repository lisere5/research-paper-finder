import csv
import os
from dotenv import load_dotenv
from backend.pinecone_helper import pc_get_index, query_vectors
import numpy as np

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")


def get_all_metadata(name=PINECONE_INDEX, top_k=5500):
    index = pc_get_index(name)

    dummy_vector = np.zeros(1536).tolist()

    response = index.query(
        vector=dummy_vector,
        top_k=top_k,
        include_values=False,
        include_metadata=True
    )

    print("retrieved all metadata from pinecone")

    authors_set = set()
    journals_set = set()

    for match in response["matches"]:
        metadata = match.get("metadata", {})
        authors_set.update(metadata.get("authors", []))
        journals_set.add(metadata.get("journal", "N/A"))

    print("saved to set")
    return sorted(authors_set), sorted(journals_set)


def save_list_to_csv(items, filename, colname):
    with open(filename, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([colname])
        for item in items:
            writer.writerow([item])


authors, journals = get_all_metadata()
save_list_to_csv(authors, "../backend/authors.csv", "author")
save_list_to_csv(journals, "../backend/journals.csv", "journal")