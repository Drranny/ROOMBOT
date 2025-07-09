from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
from sentence_similarity import SentenceSimilarityCalculator
import requests
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Hallucination Detection API",
    description="SBERT + NLI 기반 할루시네이션 판단 API",
    version="1.0.0"
)

# SBERT 계산기 (multilingual-minilm)
sim_calculator = SentenceSimilarityCalculator('paraphrase-multilingual-MiniLM-L12-v2')

# NLI 서버 주소 (nli_api.py가 실행 중이어야 함)
NLI_API_URL = "http://localhost:8004/nli"

class HallucinationRequest(BaseModel):
    sentence1: str
    sentence2: str

class HallucinationResponse(BaseModel):
    sentence1: str
    sentence2: str
    raw_score: float
    adjusted_score: float
    nli_label: str
    nli_score: float
    deduction: float
    deduction_type: str

# 점수 조정 함수 (기준 쉽게 변경 가능)
def adjust_score(raw_score: float, nli_label: str, nli_score: float) -> tuple[float, float, str]:
    """
    NLI 결과에 따라 점수 조정. (기준은 함수 내에서 쉽게 수정)
    - contradiction: 점수 * 0.5 (2배 감점)
    - neutral: 점수 * 0.75 (1배 감점)
    - entailment: 감점 없음
    """
    if nli_label == "contradiction":
        deduction = raw_score * 0.5
        return max(raw_score - deduction, 0.0), deduction, "contradiction"
    elif nli_label == "neutral":
        deduction = raw_score * 0.25
        return max(raw_score - deduction, 0.0), deduction, "neutral"
    else:
        return raw_score, 0.0, "entailment"

@app.post("/hallucination", response_model=HallucinationResponse)
async def detect_hallucination(req: HallucinationRequest):
    # 1. 유사도 계산
    sim_result = sim_calculator.calculate_similarity(req.sentence1, req.sentence2)
    if "error" in sim_result:
        raise HTTPException(status_code=500, detail=sim_result["error"])
    raw_score = sim_result["cosine_similarity"]

    # 2. NLI 판정
    try:
        nli_payload = {"premise": req.sentence1, "hypothesis": req.sentence2}
        nli_resp = requests.post(NLI_API_URL, json=nli_payload, timeout=10)
        nli_resp.raise_for_status()
        nli_data = nli_resp.json()
        nli_label = nli_data["label"]
        nli_score = nli_data["score"]
    except Exception as e:
        logger.error(f"NLI API 호출 실패: {e}")
        raise HTTPException(status_code=500, detail=f"NLI API 호출 실패: {e}")

    # 3. 점수 조정
    adjusted_score, deduction, deduction_type = adjust_score(raw_score, nli_label, nli_score)

    return HallucinationResponse(
        sentence1=req.sentence1,
        sentence2=req.sentence2,
        raw_score=round(raw_score * 100, 2),
        adjusted_score=round(adjusted_score * 100, 2),
        nli_label=nli_label,
        nli_score=nli_score,
        deduction=round(deduction * 100, 2),
        deduction_type=deduction_type
    )

@app.get("/health")
async def health():
    return {"status": "ok"} 