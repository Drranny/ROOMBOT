# ROOMBOT backend

이 디렉토리는 ROOMBOT 프로젝트의 백엔드(FastAPI 기반) 서버 코드를 포함합니다.

---
## 🏃‍♂️ 실행 방법 (Quick Start)

1. **의존성 설치**
    ```bash
    cd backend
    python3 -m venv venv
    source venv/bin/activate
    pip install -r ../requirements.txt
    pip install fastapi uvicorn pydantic openai python-dotenv
    ```
2. **환경 변수 설정**
    - 프로젝트 루트 또는 backend 폴더에 `.env` 파일 생성 후 아래와 같이 입력:
      ```
      OPENAI_API_KEY=여기에_발급받은_키_입력
      ```
3. **서버 실행**
    ```bash
    uvicorn main:app --reload
    ```
    - 실행 후: [http://localhost:8000/docs](http://localhost:8000/docs) (Swagger UI)에서 API 테스트 가능

---

## 📦 주요 파일 및 역할

- **main.py**
  - FastAPI 앱 진입점
  - 라우터(`api/routes.py`)를 앱에 등록

- **api/routes.py**
  - API 엔드포인트 정의
  - `/analyze` POST: 프롬프트를 받아 GPT 응답 반환

- **services/gpt.py**
  - OpenAI GPT API 연동 함수(`call_gpt`) 구현
  - 에러 핸들링 및 환경변수 로딩

- **services/test.py**
  - GPT API 테스트용 스크립트(직접 실행 시 동작)

---



## 🛠️ 주요 API 엔드포인트

- `POST /analyze`
  - 입력: `{ "prompt": "질문 내용" }`
  - 출력: `{ "response": "GPT 응답" }`

---

## 💡 참고
- OpenAI API 키 필요 (환경변수 또는 .env 파일)
- 추가 서비스/엔드포인트는 `services/`, `api/` 하위에 구현
- 개발/테스트용 코드는 `services/test.py` 참고
- 문의: 팀원 또는 프로젝트 최상위 README 참조
