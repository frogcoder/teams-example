from typing import Optional
from pydantic import BaseModel


class MessageRequest(BaseModel):
    title: Optional[str] = None
    text: Optional[str] = None
    image: Optional[str] = None


class Result(BaseModel):
    id: str
    url: str


class ErrorResult(BaseModel):
    status_code: int
    error_message: str
