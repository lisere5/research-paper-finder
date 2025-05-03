from fastapi import FastAPI
from pydantic import BaseModel
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
import os

load_dotenv()

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
