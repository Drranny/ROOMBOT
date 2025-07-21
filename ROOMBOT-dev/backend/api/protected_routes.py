from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from auth.dependencies import get_current_user
from typing import List
from services.db import save_user_data, get_user_data, merge_guest_to_user_data

router = APIRouter(prefix="/protected", tags=["protected"])

# Pydantic 모델들
class ProtectedData(BaseModel):
    message: str
    user_id: str
    data: dict

class UserAction(BaseModel):
    action: str
    data: dict

class UserDataRequest(BaseModel):
    data: dict

class MergeGuestDataRequest(BaseModel):
    guest_id: str
    merge_strategy: str = 'replace'

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

@router.get("/user-data")
async def get_user_data_api(current_user: dict = Depends(get_current_user)):
    """현재 인증된 사용자의 데이터를 조회합니다."""
    data = get_user_data(current_user['uid'])
    if data is None:
        raise HTTPException(status_code=404, detail="No data found for user.")
    return {"user_id": current_user['uid'], "data": data}

@router.post("/user-data")
async def save_user_data_api(request: UserDataRequest, current_user: dict = Depends(get_current_user)):
    """현재 인증된 사용자의 데이터를 저장합니다."""
    saved = save_user_data(current_user['uid'], request.data)
    return {"user_id": current_user['uid'], "data": request.data, "saved_at": str(saved.created_at)}

@router.post("/merge-guest-data")
async def merge_guest_data_api(request: MergeGuestDataRequest, current_user: dict = Depends(get_current_user)):
    """게스트 데이터를 현재 사용자 데이터로 merge합니다."""
    merged = merge_guest_to_user_data(request.guest_id, current_user['uid'], request.merge_strategy)
    if merged is None:
        raise HTTPException(status_code=404, detail="No guest data found to merge.")
    return {"user_id": current_user['uid'], "merged_data": merged.data, "merged_at": str(merged.created_at)}

@router.delete("/account")
async def delete_user_account(current_user: dict = Depends(get_current_user)):
    """사용자 계정을 삭제합니다. (위험한 작업)"""
    # 실제로는 Firebase Auth에서 사용자 계정을 삭제해야 합니다
    return {
        "message": f"사용자 {current_user['email']}의 계정이 삭제되었습니다.",
        "user_id": current_user['uid'],
        "deleted_at": "2024-01-15T10:30:00Z"
    } 