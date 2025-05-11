from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)

def query_llm(prompt: str, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content


def get_embedding(text: str, model="text-embedding-ada-002"):  # takes text, returns embedding
    response = client.embeddings.create(input=[text], model=model)
    return response.data[0].embedding


async def get_batch_embeddings(texts: list[str], model="text-embedding-3-small") -> list[list[float]]:
    response = client.embeddings.create(input=texts, model=model)
    return [e.embedding for e in response.data]
