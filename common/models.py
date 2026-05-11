from pydantic import BaseModel

class RequestModel(BaseModel):
    id: int
    query: str

class ResponseModel(BaseModel):
    id: int
    result: str
    latency: float