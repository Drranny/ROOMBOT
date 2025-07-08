from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from backend.auth.dependencies import get_current_user
from typing import List

router = APIRouter(prefix="/protected", tags=["protected"])

# Pydantic 모델들
class ProtectedData(BaseModel):
    message: str
    user_id: str
    data: dict

class UserAction(BaseModel):
    action: str
    data: dict

@router.get("/data", response_model=ProtectedData)
async def get_protected_data(current_user: dict = Depends(get_current_user)):
    """인증된 사용자만 접근할 수 있는 데이터를 반환합니다."""
    return ProtectedData(
        message="인증된 사용자만 접근 가능한 데이터입니다.",
        user_id=current_user['uid'],
        data={
            "user_email": current_user['email'],
            "display_name": current_user['display_name'],
            "access_level": "authenticated"
        }
    )

@router.post("/action")
async def perform_user_action(
    action: UserAction,
    current_user: dict = Depends(get_current_user)
):
    """인증된 사용자가 수행할 수 있는 액션입니다."""
    return {
        "message": f"사용자 {current_user['email']}이(가) {action.action}을(를) 수행했습니다.",
        "user_id": current_user['uid'],
        "action": action.action,
        "action_data": action.data,
        "status": "success"
    }

@router.get("/user-stats")
async def get_user_statistics(current_user: dict = Depends(get_current_user)):
    """사용자 통계 정보를 반환합니다."""
    # 실제로는 데이터베이스에서 사용자 통계를 가져와야 합니다
    return {
        "user_id": current_user['uid'],
        "email": current_user['email'],
        "stats": {
            "total_actions": 42,
            "last_login": "2024-01-15T10:30:00Z",
            "premium_user": True,
            "api_calls_today": 15
        }
    }

@router.delete("/account")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    """사용자 계정을 삭제합니다. (위험한 작업)"""
    # 실제로는 Firebase Auth에서 사용자 계정을 삭제해야 합니다
    return {
        "message": f"사용자 {current_user['email']}의 계정이 삭제되었습니다.",
        "user_id": current_user['uid'],
        "deleted_at": "2024-01-15T10:30:00Z"
    } 