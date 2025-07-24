from fastapi import APIRouter
from pydantic import BaseModel
from backend.services.gpt import call_gpt
from .analyze_wikipedia import router as analyze_wikipedia_router
from .wikipedia_routes import router as wikipedia_router

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/analyze")
def analyze(data: PromptRequest):
    return {"response": call_gpt(data.prompt)}

router.include_router(analyze_wikipedia_router)
router.include_router(wikipedia_router)
