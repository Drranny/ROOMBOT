# Backend API

## 설정

### OpenAI API 키 설정

GPT 요약 기능을 사용하려면 OpenAI API 키가 필요합니다.

1. **API 키 받기**:

   - https://platform.openai.com/ 접속
   - 회원가입/로그인
   - "API Keys" 메뉴 클릭
   - "Create new secret key" 클릭
   - 키 이름 입력 후 생성
   - 생성된 키를 복사 (sk-로 시작하는 키)

2. **환경변수 설정**:

   - `backend/.env` 파일을 생성하고 다음 내용을 추가:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

   - `your_openai_api_key_here` 부분을 실제 API 키로 교체

3. **API 키 확인**:
   - API 키는 `sk-`로 시작해야 합니다
   - 키가 올바르게 설정되었는지 확인하려면 서버를 재시작하세요

## 실행

```bash
cd backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
