from pydantic import BaseModel
from typing import Optional


class SearchQuery(BaseModel):
    query: str
    authors: Optional[str] = None
    journal: Optional[str] = None
    start_year: Optional[int] = None
    start_month: Optional[int] = None
    end_year: Optional[int] = None
    end_month: Optional[int] = None
