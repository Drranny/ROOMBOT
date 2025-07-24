from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any
import requests
from backend.services.sentence_similarity import SentenceSimilarityCalculator
import logging

router = APIRouter()

class AnalyzeWikipediaRequest(BaseModel):
    query: str  # 기준 문장
    keywords: List[str]
    main_keyword: str  # wikipedia 검색용 대표 키워드
    top_k: int = 5

class WikipediaCandidate(BaseModel):
    sentence: str
    matched_keywords: List[str]
    url: str
    similarity: float
    nli_label: str
    nli_score: float
    final_score: float

@router.post("/analyze/wikipedia", response_model=List[WikipediaCandidate])
def analyze_wikipedia(req: AnalyzeWikipediaRequest):
    # 1. Wikipedia 후보군 수집
    try:
        wiki_resp = requests.post(
            "http://127.0.0.1:8000/wikipedia/search",
            json={
                "main_keyword": req.main_keyword,
                "keywords": req.keywords
            },
            timeout=10
        )
        if wiki_resp.status_code != 200:
            logging.error(f"Wikipedia API status: {wiki_resp.status_code}, body: {wiki_resp.text}")
            raise HTTPException(status_code=500, detail=f"Wikipedia API 호출 실패: {wiki_resp.status_code}, {wiki_resp.text}")
        wiki_candidates = wiki_resp.json()
    except Exception as e:
        logging.exception("Wikipedia API 호출 중 예외 발생")
        raise HTTPException(status_code=500, detail=f"Wikipedia API 호출 실패: {str(e)}")

    if not wiki_candidates:
        return []

    # 2. SBERT 유사도 계산
    sim_calc = SentenceSimilarityCalculator('paraphrase-multilingual-MiniLM-L12-v2')
    for c in wiki_candidates:
        sim = sim_calc.calculate_similarity(req.query, c["sentence"])
        c["similarity"] = sim.get("cosine_similarity", 0.0)

    # 3. 상위 top_k 후보만 추림
    candidates = sorted(wiki_candidates, key=lambda x: x["similarity"], reverse=True)[:req.top_k]

    # 4. NLI 판별
    for c in candidates:
        nli_payload = {"premise": req.query, "hypothesis": c["sentence"]}
        try:
            nli_resp = requests.post("http://localhost:8004/nli", json=nli_payload, timeout=10)
            nli_data = nli_resp.json()
            c["nli_label"] = nli_data.get("label", "unknown")
            c["nli_score"] = nli_data.get("score", 0.0)
        except Exception:
            c["nli_label"] = "error"
            c["nli_score"] = 0.0

    # 5. 점수제(예시: 모순이면 -0.5, 중립이면 -0.25, 함의면 그대로)
    for c in candidates:
        deduction = 0.0
        if c["nli_label"] == "contradiction":
            deduction = 0.5
        elif c["nli_label"] == "neutral":
            deduction = 0.25
        c["final_score"] = max(c["similarity"] - deduction, 0.0)

    # 6. 최종 정렬 및 반환
    candidates = sorted(candidates, key=lambda x: x["final_score"], reverse=True)
    return [WikipediaCandidate(**c) for c in candidates] 