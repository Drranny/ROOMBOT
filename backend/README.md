# ROOMBOT Backend

FastAPI 기반 백엔드 서버

## 🚀 빠른 시작

### 1. 의존성 설치
```bash
# 가상환경 생성 (권장)
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

# 패키지 설치
pip install --upgrade pip
pip install -r ../requirements.txt

# spaCy 영어 모델 설치
python -m spacy download en_core_web_sm
```

### 2. 환경 변수 설정
```bash
# 프로젝트 루트에서
cp ../env.example .env

# .env 파일 편집
# OPENAI_API_KEY=your_actual_api_key
```

### 3. 서버 실행
```bash
# 개발 모드 (자동 재시작)
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 프로덕션 모드
python -m uvicorn main:app --host 0.0.0.0 --port 8000
```

### 4. API 문서 확인
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## 📁 프로젝트 구조

```
backend/
├── main.py              # FastAPI 앱 진입점
├── api/                 # API 라우터
│   ├── routes.py        # 메인 API 엔드포인트
│   ├── auth_routes.py   # 인증 관련 API
│   └── protected_routes.py # 보호된 리소스 API
├── services/            # 비즈니스 로직
│   ├── gpt.py          # OpenAI GPT 연동
│   ├── google_search.py # Google 검색 API
│   └── db.py           # 데이터베이스 연동
├── auth/                # 인증 관련
│   └── dependencies.py  # 인증 의존성
├── config/              # 설정 파일
│   └── firebase_config.py
└── README.md
```

## 🔧 주요 API 엔드포인트

### 텍스트 분석
- `POST /analyze`
  - 입력: `{"prompt": "분석할 텍스트"}`
  - 출력: `{"response": "분석 결과"}`

### 인증
- `POST /auth/login`
  - 입력: `{"email": "user@example.com", "password": "password"}`
  - 출력: `{"access_token": "jwt_token"}`

### 보호된 리소스
- `GET /protected/user`
  - 헤더: `Authorization: Bearer <token>`
  - 출력: `{"user": "user_info"}`

## 🐛 문제 해결

### 1. 모듈 import 오류
```bash
# PYTHONPATH 설정
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

### 2. 포트 충돌
```bash
# 다른 포트 사용
python -m uvicorn main:app --reload --port 8001
```

### 3. 가상환경 활성화 안됨
```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install -r ../requirements.txt
```

### 4. spaCy 모델 오류
```bash
# 모델 재설치
python -m spacy download en_core_web_sm --force
```

## 🧪 테스트

### 단위 테스트
```bash
# 테스트 실행
python -m pytest tests/

# 특정 테스트 파일
python -m pytest tests/test_auth.py
```

### API 테스트
```bash
# curl로 API 테스트
curl -X POST "http://localhost:8000/analyze" \
     -H "Content-Type: application/json" \
     -d '{"prompt": "테스트 문장입니다."}'
```

## 📝 개발 가이드

### 새로운 API 추가
1. `api/` 폴더에 새 라우터 파일 생성
2. `main.py`에 라우터 등록
3. 필요한 서비스 로직을 `services/`에 추가

### 환경 변수 추가
1. `env.example`에 새 변수 추가
2. `services/`에서 환경 변수 로드
3. 문서 업데이트

### 코드 스타일
- PEP 8 준수
- 타입 힌트 사용
- docstring 작성

## 🔒 보안

### 환경 변수
- 민감한 정보는 `.env` 파일에 저장
- `.env` 파일은 `.gitignore`에 포함
- 프로덕션에서는 환경 변수 사용

### 인증
- JWT 토큰 사용
- 토큰 만료 시간 설정
- CORS 설정으로 프론트엔드 연결

## 📊 모니터링

### 로그 확인
```bash
# 서버 로그 실시간 확인
tail -f logs/app.log
```

### 성능 모니터링
- FastAPI 자체 모니터링 사용
- `/docs`에서 API 성능 확인

---

**ROOMBOT Backend Team** - FastAPI 기반 AI 분석 서버
