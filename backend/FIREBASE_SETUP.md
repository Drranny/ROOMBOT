# FastAPI + Firebase Auth 설정 가이드

## 1. Firebase 프로젝트 설정

### 1.1 Firebase 콘솔에서 서비스 계정 키 생성
1. [Firebase 콘솔](https://console.firebase.google.com/)에 접속
2. `taba-roombot` 프로젝트 선택
3. 프로젝트 설정 (⚙️) → 서비스 계정 탭
4. "새 비공개 키 생성" 클릭
5. JSON 파일 다운로드

### 1.2 서비스 계정 키 파일 설정
1. 다운로드한 JSON 파일을 `backend/` 폴더에 `serviceAccountKey.json`으로 저장
2. `.gitignore`에 `serviceAccountKey.json` 추가 (보안상 중요!)

## 2. 환경 변수 설정

### 2.1 .env 파일 생성 (선택사항)
```bash
# backend/.env
FIREBASE_SERVICE_ACCOUNT_PATH=./serviceAccountKey.json
```

## 3. 의존성 설치

```bash
pip install -r requirements.txt
```

## 4. 서버 실행

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 5. API 엔드포인트

### 5.1 인증 관련 엔드포인트
- `POST /api/auth/verify-token`: Firebase ID 토큰 검증
- `GET /api/auth/me`: 현재 사용자 정보
- `GET /api/auth/profile`: 사용자 프로필 (선택사항)
- `POST /api/auth/refresh`: 토큰 새로고침

### 5.2 보호된 엔드포인트
- `GET /api/protected/data`: 인증 필요 데이터
- `POST /api/protected/action`: 사용자 액션 수행
- `GET /api/protected/user-stats`: 사용자 통계
- `DELETE /api/protected/account`: 계정 삭제

### 5.3 기존 엔드포인트
- `POST /api/analyze`: AI 분석 (인증 선택사항)

## 6. 사용 방법

### 6.1 토큰 검증
```bash
curl -X POST "http://localhost:8000/api/auth/verify-token" \
  -H "Content-Type: application/json" \
  -d '{"id_token": "firebase_id_token_here"}'
```

### 6.2 보호된 API 호출
```bash
curl -X GET "http://localhost:8000/api/protected/data" \
  -H "Authorization: Bearer your_access_token_here"
```

### 6.3 사용자 정보 조회
```bash
curl -X GET "http://localhost:8000/api/auth/me" \
  -H "Authorization: Bearer your_access_token_here"
```

## 7. 프론트엔드 연동

### 7.1 웹에서 Google 로그인 후
1. Firebase Auth에서 ID 토큰 받기
2. `/api/auth/verify-token` 엔드포인트로 토큰 전송
3. 받은 액세스 토큰으로 보호된 API 호출

### 7.2 예시 코드 (JavaScript)
```javascript
// Google 로그인 후
const idToken = await user.getIdToken();

// 백엔드로 토큰 전송
const response = await fetch('/api/auth/verify-token', {
  method: 'POST',
  headers: {
    'Content-Type': 'application/json',
  },
  body: JSON.stringify({ id_token: idToken })
});

const { access_token, user_info } = await response.json();

// 보호된 API 호출
const protectedResponse = await fetch('/api/protected/data', {
  headers: {
    'Authorization': `Bearer ${access_token}`
  }
});
```

## 8. 보안 고려사항

1. **서비스 계정 키 보안**: 절대 Git에 커밋하지 마세요
2. **환경 변수 사용**: 프로덕션에서는 환경 변수 사용
3. **HTTPS 사용**: 프로덕션에서는 반드시 HTTPS 사용
4. **토큰 만료 관리**: 클라이언트에서 토큰 만료 처리

## 9. 문제 해결

### 9.1 Firebase 초기화 오류
- 서비스 계정 키 파일 경로 확인
- Firebase 프로젝트 ID 확인

### 9.2 토큰 검증 실패
- Firebase 콘솔에서 Authentication 활성화 확인
- Google 로그인 제공자 활성화 확인

### 9.3 CORS 오류
- 프론트엔드 도메인을 Firebase 승인된 도메인에 추가

## 10. 추가 기능

향후 추가할 수 있는 기능들:
- 사용자 역할 기반 접근 제어 (RBAC)
- 토큰 블랙리스트 관리
- 사용자 활동 로깅
- API 사용량 제한
- 다중 인증 (MFA) 지원 