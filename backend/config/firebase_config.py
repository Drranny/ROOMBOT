import firebase_admin
from firebase_admin import credentials, auth
import os

# Firebase Admin SDK 초기화
def initialize_firebase():
    """Firebase Admin SDK를 초기화합니다."""
    try:
        # 이미 초기화되었는지 확인
        firebase_admin.get_app()
    except ValueError:
        # 초기화되지 않은 경우 초기화
        # 실제 서비스 계정 키 파일 경로로 변경 필요
        service_account_path = os.getenv('FIREBASE_SERVICE_ACCOUNT_PATH', 'path/to/serviceAccountKey.json')
        
        if os.path.exists(service_account_path):
            cred = credentials.Certificate(service_account_path)
            firebase_admin.initialize_app(cred)
        else:
            # 개발 환경에서는 기본 설정 사용
            firebase_admin.initialize_app()

# Firebase Auth 관련 함수들
def verify_firebase_token(id_token):
    """Firebase ID 토큰을 검증합니다."""
    try:
        decoded_token = auth.verify_id_token(id_token)
        return decoded_token
    except Exception as e:
        raise Exception(f"토큰 검증 실패: {str(e)}")

def get_user_by_uid(uid):
    """UID로 사용자 정보를 가져옵니다."""
    try:
        user = auth.get_user(uid)
        return user
    except Exception as e:
        raise Exception(f"사용자 정보 조회 실패: {str(e)}")

def create_custom_token(uid):
    """커스텀 토큰을 생성합니다."""
    try:
        custom_token = auth.create_custom_token(uid)
        return custom_token
    except Exception as e:
        raise Exception(f"커스텀 토큰 생성 실패: {str(e)}") 