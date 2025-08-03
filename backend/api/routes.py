from fastapi import APIRouter, Depends, Body
from pydantic import BaseModel
from services.gpt import call_gpt
from auth.dependencies import get_current_user_optional
import sys
import os
import json

# ai-engine 경로 추가
sys.path.append(os.path.join(os.path.dirname(__file__), '..', '..', 'ai-engine'))
from preprocessing.svo_extractor import analyze_svo
from services.db import save_svo_sentence
from services.google_search import google_search

# Wikipedia API 관련 import 추가
from .analyze_wikipedia import router as analyze_wikipedia_router
from .wikipedia_routes import router as wikipedia_router

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

# 키워드 추출 API
class KeywordRequest(BaseModel):
    text: str
    language: str = "auto"

# SVO 분석 API
class SVORequest(BaseModel):
    sentence: str

@router.post("/analyze")
async def analyze(prompt: str = Body(..., embed=True), current_user: dict = Depends(get_current_user_optional)):
    """AI 분석 엔드포인트 (인증 선택사항)"""
    user_info = current_user if current_user else {"uid": "anonymous", "email": "anonymous"}
    
    try:
        response_text = call_gpt(prompt)
        return {
            "response": response_text,
            "user": user_info,
            "authenticated": current_user is not None
        }
    except Exception as e:
        return {
            "response": f"오류가 발생했습니다: {str(e)}",
            "user": user_info,
            "authenticated": current_user is not None
        }

@router.post("/svo")
def svo_analysis(data: SVORequest):
    """SVO 분석 엔드포인트"""
    try:
        # 언어 자동 감지
        if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in data.sentence):
            language = "ko"
            method = "okt"
        else:
            language = "en"
            method = "spacy"
        
        # SVO 분석 실행
        result = analyze_svo(data.sentence, language, method=method)
        
        return {
            "sentence": data.sentence,
            "language": language,
            "svo": result
        }
    except Exception as e:
        return {"error": str(e)}

@router.post("/keywords")
def keyword_analysis(data: KeywordRequest):
    """키워드 추출 엔드포인트"""
    try:
        # 언어 자동 감지
        if data.language == "auto":
            if any('\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af' for char in data.text):
                language = "ko"
                method = "okt"
            else:
                language = "en"
                method = "spacy"
        else:
            language = data.language
            method = "okt" if language == "ko" else "spacy"
        
        # 키워드 분석 실행
        result = analyze_svo(data.text, language, method=method)
        
        return {
            "text": data.text,
            "language": language,
            "keywords": result.get("keywords", [])
        }
    except Exception as e:
        return {"error": str(e)}

# 키워드 저장 API
class SaveKeywordRequest(BaseModel):
    text: str
    language: str
    result: str

@router.post("/save_keywords")
def save_keywords(data: SaveKeywordRequest):
    """키워드 결과 저장 엔드포인트"""
    try:
        # 데이터베이스에 저장
        save_svo_sentence(data.text, data.language, data.result)
        return {"message": "키워드 결과가 저장되었습니다"}
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

def analyze_svo_with_gpt(text: str):
    """
    GPT를 사용한 SVO 분석
    """
    # 언어 감지
    korean_chars = sum(1 for char in text if '\u3131' <= char <= '\u3163' or '\uac00' <= char <= '\ud7af')
    english_chars = sum(1 for char in text if char.isalpha() and ord(char) < 128)
    language = "ko" if korean_chars > english_chars else "en"
    
    if language == "en":
        prompt = f"""
Analyze the Subject, Verb, and Object of the following sentence.

Sentence: "{text}"

Please respond in the following JSON format:
{{
    "sentence": "original sentence",
    "language": "en",
    "svo": {{
        "subject": "subject",
        "verb": "verb/predicate",
        "object": "object (null if none)",
        "predicate_type": "VV",
        "has_object": true/false
    }}
}}

Notes:
1. Extract the complete subject including articles and modifiers
2. Set object to null if there is no object
3. Include auxiliary verbs and linking verbs as part of the verb
4. Respond only in JSON format without any other explanation
"""
    else:
        prompt = f"""
다음 문장의 주어(Subject), 동사(Verb), 목적어(Object)를 분석해주세요.

문장: "{text}"

다음 JSON 형식으로 응답해주세요:
{{
    "sentence": "원본 문장",
    "language": "ko",
    "svo": {{
        "subject": "주어",
        "verb": "동사/서술어",
        "object": "목적어 (없으면 null)",
        "predicate_type": "VV",
        "has_object": true/false
    }}
}}

주의사항:
1. 한국어 문장의 경우 조사를 포함한 정확한 주어를 추출하세요
2. 목적어가 없는 경우 null로 설정하세요
3. 서술격 조사(이다, 있다, 없다 등)도 동사로 인식하세요
4. JSON 형식만 응답하고 다른 설명은 하지 마세요
"""
    
    try:
        # GPT 호출
        gpt_response = call_gpt(prompt)
        
        # JSON 파싱 시도
        try:
            # 응답에서 JSON 부분만 추출
            start_idx = gpt_response.find('{')
            end_idx = gpt_response.rfind('}') + 1
            if start_idx != -1 and end_idx != 0:
                json_str = gpt_response[start_idx:end_idx]
                result = json.loads(json_str)
                return result
            else:
                raise ValueError("JSON 형식을 찾을 수 없습니다")
        except json.JSONDecodeError:
            # JSON 파싱 실패 시 기본 형식으로 반환
            return {
                "sentence": text,
                "language": "ko",
                "svo": {
                    "subject": "주어",
                    "verb": "동사",
                    "object": "없음",
                    "predicate_type": "VV",
                    "has_object": False
                },
                "gpt_response": gpt_response  # 디버깅용
            }
    except Exception as e:
        return {
            "sentence": text,
            "language": "ko",
            "svo": {
                "subject": "주어",
                "verb": "동사",
                "object": "없음",
                "predicate_type": "VV",
                "has_object": False
            },
            "error": str(e)
        }

# Wikipedia API 라우터들 추가
router.include_router(analyze_wikipedia_router)
router.include_router(wikipedia_router)
