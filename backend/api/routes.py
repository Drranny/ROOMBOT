from fastapi import APIRouter
from pydantic import BaseModel
from services.gpt import call_gpt
import sys
import os

# ai-engine 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai-engine'))
from preprocessing.svo_extractor import analyze_svo
from services.db import save_svo_sentence
from services.google_search import google_search

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

# 구조문장 저장 API
class SVOSaveRequest(BaseModel):
    text: str
    language: str
    result: str

@router.post("/save_svo")
def save_svo(data: SVOSaveRequest):
    try:
        svo = save_svo_sentence(data.text, data.language, data.result)
        return {"id": svo.id, "text": svo.text, "language": svo.language, "result": svo.result}
    except Exception as e:
        return {"error": str(e)}

# Google Custom Search API
class SearchRequest(BaseModel):
    query: str

@router.post("/google_search")
def search(data: SearchRequest):
    try:
        result = google_search(data.query)
        return result
    except Exception as e:
        return {"error": str(e)}

# 검색결과 저장 (임시 메모리)
search_results_store = []

class SearchResult(BaseModel):
    query: str
    results: list

@router.post("/search-results")
def save_search_result(data: SearchResult):
    search_results_store.append(data)
    return {"message": "저장 완료", "count": len(search_results_store)}

@router.get("/search-results")
def get_search_results():
    return search_results_store
