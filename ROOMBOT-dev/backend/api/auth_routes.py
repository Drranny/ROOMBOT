from fastapi import APIRouter, HTTPException, status, Depends
from pydantic import BaseModel
from auth.dependencies import get_current_user, get_current_user_optional
from config.firebase_config import verify_firebase_token, create_custom_token
from typing import Optional

router = APIRouter(prefix="/auth", tags=["authentication"])

# Pydantic 모델들
class TokenRequest(BaseModel):
    id_token: str

class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user_info: dict

class UserInfo(BaseModel):
    uid: str
    email: str
    display_name: Optional[str] = None
    photo_url: Optional[str] = None
    email_verified: bool

@router.post("/verify-token", response_model=TokenResponse)
async def verify_token(token_request: TokenRequest):
    """Firebase ID 토큰을 검증하고 사용자 정보를 반환합니다."""
    try:
        # Firebase ID 토큰 검증
        decoded_token = verify_firebase_token(token_request.id_token)
        
        # 사용자 정보 구성
        user_info = {
            'uid': decoded_token['uid'],
            'email': decoded_token.get('email', ''),
            'display_name': decoded_token.get('name', ''),
            'photo_url': decoded_token.get('picture', ''),
            'email_verified': decoded_token.get('email_verified', False)
        }
        
        # 커스텀 토큰 생성 (선택사항)
        custom_token = create_custom_token(decoded_token['uid'])
        
        return TokenResponse(
            access_token=custom_token.decode(),
            user_info=user_info
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail=f"토큰 검증 실패: {str(e)}"
        )

@router.get("/me", response_model=UserInfo)
async def get_current_user_info(current_user: dict = Depends(get_current_user)):
    """현재 인증된 사용자의 정보를 반환합니다."""
    return UserInfo(**current_user)

@router.get("/profile")
async def get_user_profile(current_user: Optional[dict] = Depends(get_current_user_optional)):
    """사용자 프로필 정보를 반환합니다. (인증 선택사항)"""
    if current_user is None:
        return {"message": "인증되지 않은 사용자", "authenticated": False}
    
    return {
        "authenticated": True,
        "user": current_user,
        "message": "인증된 사용자"
    }

@router.post("/refresh")
async def refresh_token(current_user: dict = Depends(get_current_user)):
    """토큰을 새로고침합니다."""
    try:
        # 새로운 커스텀 토큰 생성
        custom_token = create_custom_token(current_user['uid'])
        
        return {
            "access_token": custom_token.decode(),
            "token_type": "bearer",
            "message": "토큰이 새로고침되었습니다."
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"토큰 새로고침 실패: {str(e)}"
        ) 