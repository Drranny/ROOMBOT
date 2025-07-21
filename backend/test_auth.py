#!/usr/bin/env python3
"""
Firebase Auth 테스트 스크립트
실제 Firebase ID 토큰이 필요합니다.
"""

import requests
import json

# API 기본 URL
BASE_URL = "http://localhost:8000/api"

def test_health_check():
    """헬스 체크 테스트"""
    try:
        response = requests.get("http://localhost:8000/health")
        print("✅ 헬스 체크:", response.json())
        return True
    except Exception as e:
        print("❌ 헬스 체크 실패:", e)
        return False

def test_analyze_without_auth():
    """인증 없이 분석 API 테스트"""
    try:
        data = {"prompt": "세종대왕은 언제 태어났어?"}
        response = requests.post(f"{BASE_URL}/analyze", json=data)
        print("✅ 분석 API (인증 없음):", response.json())
        return True
    except Exception as e:
        print("❌ 분석 API 실패:", e)
        return False

def test_verify_token(firebase_id_token):
    """Firebase ID 토큰 검증 테스트"""
    try:
        data = {"id_token": firebase_id_token}
        response = requests.post(f"{BASE_URL}/auth/verify-token", json=data)
        if response.status_code == 200:
            result = response.json()
            print("✅ 토큰 검증 성공:", result)
            return result.get("access_token")
        else:
            print("❌ 토큰 검증 실패:", response.json())
            return None
    except Exception as e:
        print("❌ 토큰 검증 오류:", e)
        return None

def test_protected_api(access_token):
    """보호된 API 테스트"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/protected/data", headers=headers)
        if response.status_code == 200:
            print("✅ 보호된 API 성공:", response.json())
            return True
        else:
            print("❌ 보호된 API 실패:", response.json())
            return False
    except Exception as e:
        print("❌ 보호된 API 오류:", e)
        return False

def test_user_info(access_token):
    """사용자 정보 조회 테스트"""
    try:
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(f"{BASE_URL}/auth/me", headers=headers)
        if response.status_code == 200:
            print("✅ 사용자 정보 조회 성공:", response.json())
            return True
        else:
            print("❌ 사용자 정보 조회 실패:", response.json())
            return False
    except Exception as e:
        print("❌ 사용자 정보 조회 오류:", e)
        return False

def main():
    """메인 테스트 함수"""
    print("🚀 Firebase Auth 테스트 시작\n")
    
    # 1. 헬스 체크
    if not test_health_check():
        print("서버가 실행되지 않았습니다. uvicorn main:app --reload를 실행하세요.")
        return
    
    # 2. 인증 없이 분석 API 테스트
    test_analyze_without_auth()
    
    print("\n" + "="*50)
    print("Firebase ID 토큰이 필요합니다.")
    print("웹에서 Google 로그인 후 ID 토큰을 입력하세요.")
    print("="*50)
    
    # 3. Firebase ID 토큰 입력 (실제 테스트 시)
    firebase_id_token = input("\nFirebase ID 토큰을 입력하세요 (Enter로 건너뛰기): ").strip()
    
    if firebase_id_token:
        # 4. 토큰 검증
        access_token = test_verify_token(firebase_id_token)
        
        if access_token:
            # 5. 보호된 API 테스트
            test_protected_api(access_token)
            
            # 6. 사용자 정보 조회
            test_user_info(access_token)
    else:
        print("토큰 검증 테스트를 건너뜁니다.")
    
    print("\n✅ 테스트 완료!")

if __name__ == "__main__":
    main() 