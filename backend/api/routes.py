from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.gpt import call_gpt

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/analyze")
def analyze(data: PromptRequest):
    return {"response": call_gpt(data.prompt)}
