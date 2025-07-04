# backend/api/routes.py
from fastapi import APIRouter
from pydantic import BaseModel
from ai_engine.preprocessing.svo_extractor import analyze_svo_from_text

router = APIRouter()

class AnalyzeRequest(BaseModel):
    text: str

@router.post("/analyze")
def analyze(request: AnalyzeRequest):
    return {"result": analyze_svo_from_text(request.text)}
