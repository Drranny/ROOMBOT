from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from sentence_similarity import SentenceSimilarityCalculator
import logging

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 초기화
app = FastAPI(
    title="SBERT Multilingual MPNet Sentence Similarity API",
    description="paraphrase-multilingual-mpnet-base-v2 모델을 이용한 다국어 문장 유사도 계산 API",
    version="1.0.0"
)

# SBERT 계산기 초기화 (paraphrase-multilingual-mpnet-base-v2 모델)
calculator = SentenceSimilarityCalculator('paraphrase-multilingual-mpnet-base-v2')

# Pydantic 모델들
class SimilarityRequest(BaseModel):
    sentence1: str
    sentence2: str
    model_name: Optional[str] = 'paraphrase-multilingual-mpnet-base-v2'

class BatchSimilarityRequest(BaseModel):
    sentence_pairs: List[List[str]]  # [[sentence1, sentence2], ...]
    model_name: Optional[str] = 'paraphrase-multilingual-mpnet-base-v2'

class FindSimilarRequest(BaseModel):
    query_sentence: str
    candidate_sentences: List[str]
    top_k: Optional[int] = 5
    model_name: Optional[str] = 'paraphrase-multilingual-mpnet-base-v2'

class SimilarityResponse(BaseModel):
    sentence1: str
    sentence2: str
    cosine_similarity: float
    euclidean_distance: float
    similarity_percentage: float
    model_used: str

@app.get("/")
async def root():
    """API 루트 엔드포인트"""
    return {
        "message": "SBERT Multilingual MPNet Sentence Similarity API",
        "version": "1.0.0",
        "model": "paraphrase-multilingual-mpnet-base-v2",
        "endpoints": {
            "/similarity": "두 문장 간 유사도 계산",
            "/batch-similarity": "여러 문장 쌍의 유사도 일괄 계산",
            "/find-similar": "쿼리 문장과 가장 유사한 문장들 찾기"
        }
    }

@app.post("/similarity", response_model=SimilarityResponse)
async def calculate_similarity(request: SimilarityRequest):
    """두 문장 간의 유사도를 계산합니다."""
    global calculator
    try:
        model_name = request.model_name if request.model_name is not None else 'paraphrase-multilingual-mpnet-base-v2'
        if model_name != calculator.model_name:
            calculator = SentenceSimilarityCalculator(model_name)
        
        result = calculator.calculate_similarity(request.sentence1, request.sentence2)
        
        if "error" in result:
            raise HTTPException(status_code=500, detail=result["error"])
        
        return SimilarityResponse(**result)
        
    except Exception as e:
        logger.error(f"Error in similarity calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch-similarity")
async def calculate_batch_similarity(request: BatchSimilarityRequest):
    """여러 문장 쌍의 유사도를 일괄 계산합니다."""
    global calculator
    try:
        model_name = request.model_name if request.model_name is not None else 'paraphrase-multilingual-mpnet-base-v2'
        if model_name != calculator.model_name:
            calculator = SentenceSimilarityCalculator(model_name)
        
        sentence_pairs = [(pair[0], pair[1]) for pair in request.sentence_pairs]
        results = calculator.calculate_batch_similarity(sentence_pairs)
        
        return {
            "results": results,
            "total_pairs": len(results),
            "model_used": calculator.model_name
        }
        
    except Exception as e:
        logger.error(f"Error in batch similarity calculation: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/find-similar")
async def find_most_similar(request: FindSimilarRequest):
    """쿼리 문장과 가장 유사한 문장들을 찾습니다."""
    global calculator
    try:
        model_name = request.model_name if request.model_name is not None else 'paraphrase-multilingual-mpnet-base-v2'
        if model_name != calculator.model_name:
            calculator = SentenceSimilarityCalculator(model_name)
        
        top_k = request.top_k if request.top_k is not None else 5
        results = calculator.find_most_similar(
            request.query_sentence,
            request.candidate_sentences,
            top_k
        )
        
        return {
            "query_sentence": request.query_sentence,
            "results": results,
            "total_candidates": len(request.candidate_sentences),
            "top_k": top_k,
            "model_used": calculator.model_name
        }
        
    except Exception as e:
        logger.error(f"Error in finding most similar sentences: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크 엔드포인트"""
    return {"status": "healthy", "model_loaded": True, "model": "paraphrase-multilingual-mpnet-base-v2"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8002) 