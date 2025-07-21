from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from config.firebase_config import verify_firebase_token, get_user_by_uid
import firebase_admin
from firebase_admin import auth

# HTTP Bearer 토큰 스키마
security = HTTPBearer()

async def get_current_user(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """현재 인증된 사용자를 가져옵니다."""
    try:
        # Firebase ID 토큰 검증
        decoded_token = verify_firebase_token(credentials.credentials)
        uid = decoded_token['uid']
        
        # 사용자 정보 가져오기
        user = get_user_by_uid(uid)
        
        return {
            'uid': user.uid,
            'email': user.email,
            'display_name': user.display_name,
            'photo_url': user.photo_url,
            'email_verified': user.email_verified
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="유효하지 않은 인증 토큰",
            headers={"WWW-Authenticate": "Bearer"},
        )

async def get_current_user_optional(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """선택적으로 현재 인증된 사용자를 가져옵니다. (인증이 실패해도 None 반환)"""
    try:
        return await get_current_user(credentials)
    except HTTPException:
        return None 