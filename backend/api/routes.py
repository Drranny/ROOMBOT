from fastapi import APIRouter, Depends
from pydantic import BaseModel
from services.gpt import call_gpt
from auth.dependencies import get_current_user_optional

router = APIRouter()

class PromptRequest(BaseModel):
    prompt: str

@router.post("/analyze")
def analyze(data: PromptRequest, current_user: dict = Depends(get_current_user_optional)):
    """AI 분석 엔드포인트 (인증 선택사항)"""
    user_info = current_user if current_user else {"uid": "anonymous", "email": "anonymous"}
    
    return {
        "response": call_gpt(data.prompt),
        "user": user_info,
        "authenticated": current_user is not None
    }
