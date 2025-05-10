from create_embeddings import get_batch_embeddings
from pinecone_helper import upsert_document_vectors
import feedparser
import asyncio
import os
from dotenv import load_dotenv

load_dotenv()

PINECONE_INDEX = os.getenv("PINECONE_INDEX")

"""
SAMPLE API REQUEST TO ARXIV
url = 'http://export.arxiv.org/api/query?search_query=all:electron&start=0&max_results=1'
data = urllib.request.urlopen(url)
print(data.read().decode('utf-8'))
"""

arxiv_categories = [
    # Computer Science
    "cs.AI", "cs.CL", "cs.CV", "cs.LG", "cs.NE", "cs.RO", "cs.DS", "cs.CR",
    "cs.NI", "cs.SE", "cs.PL", "cs.OS", "cs.DB", "cs.HC", "cs.SI", "cs.CY",
    "cs.MA", "cs.LO", "cs.FL", "cs.GT", "cs.DC", "cs.SY", "cs.ET", "cs.CE",
    "cs.AR", "cs.GL", "cs.OH",

    # Statistics
    "stat.ML", "stat.AP", "stat.CO", "stat.TH", "stat.ME", "stat.OT",

    # Mathematics
    "math.AG", "math.AP", "math.AT", "math.CA", "math.CO", "math.CT",
    "math.CV", "math.DG", "math.DS", "math.FA", "math.GM", "math.GN",
    "math.GR", "math.GT", "math.HO", "math.IT", "math.KT", "math.LO",
    "math.MG", "math.MP", "math.NA", "math.NT", "math.OA", "math.OC",
    "math.PR", "math.QA", "math.RA", "math.RT", "math.SG", "math.SP", "math.ST",

    # Physics
    "physics.acc-ph", "physics.app-ph", "physics.atom-ph", "physics.atm-clus",
    "physics.bio-ph", "physics.chem-ph", "physics.class-ph", "physics.comp-ph",
    "physics.data-an", "physics.ed-ph", "physics.flu-dyn", "physics.gen-ph",
    "physics.geo-ph", "physics.hist-ph", "physics.ins-det", "physics.med-ph",
    "physics.optics", "physics.plasm-ph", "physics.pop-ph", "physics.soc-ph",
    "physics.space-ph",

    # Quantitative Biology
    "q-bio.BM", "q-bio.CB", "q-bio.GN", "q-bio.MN", "q-bio.NC", "q-bio.OT",
    "q-bio.PE", "q-bio.QM", "q-bio.SC", "q-bio.TO",

    # Quantitative Finance
    "q-fin.CP", "q-fin.EC", "q-fin.GN", "q-fin.MF", "q-fin.PM", "q-fin.PR",
    "q-fin.RM", "q-fin.ST", "q-fin.TR",

    # Economics
    "econ.EM", "econ.GN", "econ.TH",

    # Electrical Engineering and Systems Science
    "eess.AS", "eess.IV", "eess.SP", "eess.SY"
]

papers = set()


def fetch_arxiv(cat, max_per_cat=20):
    res = []

    print(f"Category: {cat}")
    url = f"http://export.arxiv.org/api/query?search_query=cat:{cat}&start=0&max_results={max_per_cat}&sortBy=relevance&sortOrder=ascending"
    feed = feedparser.parse(url)

    for entry in feed.entries:
        link = entry.get('id', None)

        if link is not None:
            if link in papers:
                continue

            papers.add(link)
            print(f"***Paper: {link}")

            title = entry.get('title', None)
            abstract = entry.get('summary', None)
            authors = [a.get("name") for a in entry.get("authors", [])]

            entry_dict = {
                'link': link,
                'published_date': entry.get('published', None),
                'published_year': entry.get("published_parsed").tm_year if entry.get("published_parsed") else None,
                'published_month': entry.get("published_parsed").tm_mon if entry.get("published_parsed") else None,
                'published_day': entry.get("published_parsed").tm_mday if entry.get("published_parsed") else None,
                'title': title,
                'abstract': abstract,
                'authors': authors,
                'text': f"Title: {title}, Abstract: {abstract}"
            }

            res.append(entry_dict)
    print()
    return res


# entries = fetch_arxiv(['cs.ai'], 1) # TESTING PURPOSES

async def main():
    vectors = []

    for i in range(0, len(arxiv_categories), 5):
        batch_categories = arxiv_categories[i:i+5]
        entries = []
        for cat in batch_categories:
            entries.extend(fetch_arxiv(cat))

        # get embeddings
        texts = [entry['text'] for entry in entries]
        embeddings = await get_batch_embeddings(texts)

        # generate vectors to be inserted
        for entry, embedding in zip(entries, embeddings):
            doc_uid = entry['link'].encode("utf-8").hex()
            vector = {
                "id": doc_uid,
                "values": embedding,
                "metadata": {
                    "title": entry["title"],
                    "abstract": entry["abstract"],
                    "authors": entry["authors"],
                    "published_year": entry["published_year"],
                    "journal": entry.get("journal", "unknown")
                }
            }
            vectors.append(vector)

        if len(vectors) == 100:
            try:
                upsert_document_vectors(PINECONE_INDEX, vectors)
            except Exception as e:
                print(f"[ERROR] Failed to upsert batch: {e}")
            vectors = []

    if vectors:
        try:
            upsert_document_vectors(PINECONE_INDEX, vectors)
        except Exception as e:
            print(f"[ERROR] Failed to upsert batch: {e}")

if __name__ == "__main__":
    asyncio.run(main())
