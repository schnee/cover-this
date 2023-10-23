# models.py

from langchain.pydantic_v1 import BaseModel, Field
from typing import List

class QuestionList(BaseModel):
    assessment: str = Field(description="Suitability assessment") 
    questions: List[str] = Field(description="List of questions")
