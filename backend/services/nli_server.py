#!/usr/bin/env python3
"""
NLI (Natural Language Inference) 서버
문장 간의 논리적 관계를 판단하는 서버
"""

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict, Any, Optional
import uvicorn
import logging
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import torch
import numpy as np

# 로깅 설정
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI 앱 생성
app = FastAPI(title="NLI Server", description="Natural Language Inference Server")

# NLI 모델 초기화
class NLIModel:
    def __init__(self, model_name: str = "microsoft/DialoGPT-medium"):
        """
        NLI 모델 초기화
        
        Args:
            model_name (str): 사용할 NLI 모델명
        """
        self.model_name = model_name
        logger.info(f"Loading NLI model: {model_name}")
        
        try:
            # 토크나이저와 모델 로드
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModelForSequenceClassification.from_pretrained(model_name)
            logger.info("NLI model loaded successfully")
        except Exception as e:
            logger.error(f"Error loading NLI model: {str(e)}")
            # 기본값으로 설정
            self.tokenizer = None
            self.model = None
    
    def predict_nli(self, premise: str, hypothesis: str) -> Dict[str, Any]:
        """
        NLI 예측 수행
        
        Args:
            premise (str): 전제 문장
            hypothesis (str): 가설 문장
            
        Returns:
            Dict[str, Any]: NLI 결과
        """
        if self.model is None or self.tokenizer is None:
            return {
                "error": "NLI model not loaded",
                "premise": premise,
                "hypothesis": hypothesis,
                "prediction": "error",
                "confidence": 0.0
            }
        
        try:
            # 문장을 토큰화
            inputs = self.tokenizer(
                premise, 
                hypothesis, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512
            )
            
            # 예측 수행
            with torch.no_grad():
                outputs = self.model(**inputs)
                probabilities = torch.softmax(outputs.logits, dim=-1)
                prediction = torch.argmax(probabilities, dim=-1).item()
                confidence = probabilities[0][prediction].item()
            
            # 라벨 매핑 (모델에 따라 다를 수 있음)
            labels = ["contradiction", "neutral", "entailment"]
            predicted_label = labels[prediction] if prediction < len(labels) else "unknown"
            
            return {
                "premise": premise,
                "hypothesis": hypothesis,
                "prediction": predicted_label,
                "confidence": round(confidence, 4),
                "probabilities": {
                    "contradiction": round(probabilities[0][0].item(), 4),
                    "neutral": round(probabilities[0][1].item(), 4),
                    "entailment": round(probabilities[0][2].item(), 4)
                }
            }
            
        except Exception as e:
            logger.error(f"Error in NLI prediction: {str(e)}")
            return {
                "error": str(e),
                "premise": premise,
                "hypothesis": hypothesis,
                "prediction": "error",
                "confidence": 0.0
            }

# NLI 모델 인스턴스 생성
nli_model = NLIModel()

# Pydantic 모델들
class NLIRequest(BaseModel):
    premise: str
    hypothesis: str

class NLIResponse(BaseModel):
    premise: str
    hypothesis: str
    prediction: str
    confidence: float
    probabilities: Dict[str, float]
    error: Optional[str] = None

class BatchNLIRequest(BaseModel):
    pairs: List[Dict[str, str]]

class BatchNLIResponse(BaseModel):
    results: List[NLIResponse]

# API 엔드포인트들
@app.get("/")
async def root():
    """서버 상태 확인"""
    return {"message": "NLI Server is running", "status": "healthy"}

@app.post("/predict", response_model=NLIResponse)
async def predict_nli(request: NLIRequest):
    """단일 NLI 예측"""
    try:
        result = nli_model.predict_nli(request.premise, request.hypothesis)
        return NLIResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/batch_predict", response_model=BatchNLIResponse)
async def batch_predict_nli(request: BatchNLIRequest):
    """배치 NLI 예측"""
    try:
        results = []
        for pair in request.pairs:
            result = nli_model.predict_nli(pair["premise"], pair["hypothesis"])
            results.append(NLIResponse(**result))
        return BatchNLIResponse(results=results)
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def health_check():
    """헬스 체크"""
    return {
        "status": "healthy",
        "model_loaded": nli_model.model is not None,
        "model_name": nli_model.model_name
    }

if __name__ == "__main__":
    # 서버 실행
    uvicorn.run(
        "nli_server:app",
        host="0.0.0.0",
        port=8001,  # 메인 백엔드와 다른 포트 사용
        reload=True,
        log_level="info"
    )
