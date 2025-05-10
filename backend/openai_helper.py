from openai import OpenAI
from dotenv import load_dotenv
import os

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
client = OpenAI(api_key=OPENAI_API_KEY)


def create_prompt(query: str, docs: dict):
    context = "\n---\n".join(doc['metadata']['text'] for doc in docs["matches"])
    prompt = f"""
    Answer the question Q based on the following Context
    Context:
    {context}

    Q: {query}
    """

    return prompt


def query_llm(prompt: str, model="gpt-3.5-turbo"):
    response = client.chat.completions.create(
        model=model,
        messages=[
            {"role": "user", "content": prompt}
        ],
    )

    return response.choices[0].message.content
