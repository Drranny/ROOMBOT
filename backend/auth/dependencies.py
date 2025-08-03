from fastapi import HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Firebase Admin SDK를 선택적으로 import
try:
    from config.firebase_config import verify_firebase_token, get_user_by_uid
    import firebase_admin
    from firebase_admin import auth
    FIREBASE_AVAILABLE = True
except ImportError:
    print("Warning: Firebase Admin SDK not available. Authentication will be disabled.")
    FIREBASE_AVAILABLE = False

security = HTTPBearer()

def get_current_user_optional(credentials: HTTPAuthorizationCredentials = None):
    """선택적 사용자 인증 (Firebase가 없어도 작동)"""
    if not FIREBASE_AVAILABLE:
        return None
    
    if not credentials:
        return None
    
    try:
        # Firebase ID 토큰 검증
        decoded_token = verify_firebase_token(credentials.credentials)
        
        # 사용자 정보 가져오기
        user = get_user_by_uid(decoded_token['uid'])
        
        return user
    except Exception as e:
        print(f"Authentication error: {e}")
        return None

def get_current_user(credentials: HTTPAuthorizationCredentials = security):
    """필수 사용자 인증 (Firebase가 없으면 오류)"""
    if not FIREBASE_AVAILABLE:
        raise HTTPException(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            detail="Authentication service not available"
        )
    
    if not credentials:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    try:
        # Firebase ID 토큰 검증
        decoded_token = verify_firebase_token(credentials.credentials)
        
        # 사용자 정보 가져오기
        user = get_user_by_uid(decoded_token['uid'])
        
        if not user:
            raise HTTPException(
                status_code=status.HTTP_401_UNAUTHORIZED,
                detail="User not found",
                headers={"WWW-Authenticate": "Bearer"},
            )
        
        return user
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
            headers={"WWW-Authenticate": "Bearer"},
        ) 