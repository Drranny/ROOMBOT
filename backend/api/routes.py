from fastapi import APIRouter
from pydantic import BaseModel
from services.gpt import call_gpt
import sys
import os

# ai-engine 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai-engine'))
from preprocessing.svo_extractor import analyze_svo

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

class SVORequest(BaseModel):
    text: str
    language: str = "auto"  # auto, ko, en

@router.post("/analyze")
def analyze(data: PromptRequest):
    return {"response": call_gpt(data.prompt)}

@router.post("/svo")
def svo_analysis(data: SVORequest):
    try:
        # 언어 자동 감지
        if data.language == "auto":
            # 간단한 한국어 감지
            if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in data.text):
                data.language = "ko"
            else:
                data.language = "en"
        
        # SVO 분석 실행
        result = analyze_svo(data.text, data.language)
        return result
    except Exception as e:
        return {"error": str(e)}
