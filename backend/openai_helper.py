from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def chunk_text(text: str, max_tokens=15000):
    approx_char_limit = max_tokens * 2
    chunks = []

    for i in range(0, len(text), approx_char_limit):
        chunks.append(text[i:i + approx_char_limit])

    return chunks


def query_llm(prompt: str, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content


def query_llm_in_chunks(text: str, model="gpt-3.5-turbo"):
    chunks = chunk_text(text)
    summaries = []

    for chunk in chunks:
        prompt = f"""Summarize the following research paper or portion of a research paper. 
        Be high level, use no more than 8 sentences. 
        The summary must be in paragraph form. 
        
        Research Paper: {chunk}
        """
        summary = query_llm(prompt, model)
        summaries.append(summary)

    if len(chunks) == 1:
        return summaries[0]

    prompt = f"""
    Below contains summaries of different portions of a research paper. 
    Summarize the summaries using no more than 8 sentences.
    The summary must be in paragraph form.
    
    Summaries: {summaries}
    """
    summary = query_llm(prompt, model)

    return summary


def get_embedding(text: str, model="text-embedding-ada-002"):  # takes text, returns embedding
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


async def get_batch_embeddings(texts: list[str], model="text-embedding-3-small") -> list[list[float]]:
    response = client.embeddings.create(input=texts, model=model)
    return [e.embedding for e in response.data]
