import os
from pinecone import Pinecone
from pinecone_helper import pc_create_index
from dotenv import load_dotenv

load_dotenv()
PINECONE_API_KEY = os.getenv("PINECONE_API_KEY")
PINECONE_INDEX = os.getenv("PINECONE_INDEX")

# pinecone setup
pc = Pinecone(api_key=PINECONE_API_KEY)

name = PINECONE_INDEX
dimension = 1536
metric = "cosine"
cloud = "aws"
region = "us-east-1"

created_index = pc_create_index(name, dimension, metric, cloud, region)

print(created_index)