# ROOMBOT

AI 기반 키워드 추출 및 분석 시스템

## 🚀 빠른 시작 (Quick Start)

### 1. 저장소 클론
```bash
git clone <repository-url>
cd ROOMBOT
```

### 2. 자동 설치 (권장)
```bash
chmod +x scripts/install.sh
./scripts/install.sh
```

### 3. 수동 설치 (자동 설치가 안 될 경우)

#### Python 환경 설정
```bash
# 가상환경 생성
python3 -m venv venv
source venv/bin/activate  # macOS/Linux
# 또는 venv\Scripts\activate  # Windows

# 의존성 설치
pip install --upgrade pip
pip install -r requirements.txt

# spaCy 영어 모델 설치
python -m spacy download en_core_web_sm
```

#### Java 설치 (konlpy 사용을 위해)
```bash
# macOS
brew install openjdk@11
export JAVA_HOME=$(/usr/libexec/java_home -v 11)

# Ubuntu
sudo apt-get install openjdk-11-jdk

# Windows
# https://adoptium.net/ 에서 Java 11 다운로드
```

#### Node.js 환경 설정
```bash
cd frontend
npm install
cd ..
```

### 4. 환경 변수 설정
```bash
# 환경 변수 템플릿 복사
cp env.example .env

# .env 파일을 편집하여 실제 값 입력
# 특히 OPENAI_API_KEY는 필수
```

### 5. 개발 서버 실행

#### 백엔드 실행
```bash
cd backend
python -m uvicorn main:app --reload --host 0.0.0.0 --port 8000
```
- API 문서: http://localhost:8000/docs

#### 프론트엔드 실행
```bash
cd frontend
npm run dev
```
- 웹사이트: http://localhost:3000

## 🛠️ 프로젝트 구조

```
ROOMBOT/
├── ai-engine/          # AI 키워드 추출 엔진
│   └── preprocessing/
│       ├── keyword_extractor.py
│       └── ...
├── backend/            # FastAPI 백엔드
│   ├── main.py
│   ├── api/
│   └── services/
├── frontend/           # Next.js 프론트엔드
│   ├── src/
│   └── package.json
├── scripts/            # 설치 및 배포 스크립트
└── requirements.txt    # Python 의존성
```

## 🔧 주요 기능

### 키워드 추출
- 한국어/영어 텍스트 분석
- 형태소 분석 기반 키워드 추출
- 문장 길이에 따른 적응형 처리

### API 엔드포인트
- `POST /analyze`: 텍스트 분석
- `POST /auth/login`: 사용자 인증
- `GET /protected/user`: 보호된 리소스

## 🐛 문제 해결

### 자주 발생하는 문제들

#### 1. konlpy 초기화 실패
```bash
# Java 설치 확인
java -version

# JAVA_HOME 설정 (macOS)
export JAVA_HOME=$(/usr/libexec/java_home -v 11)
```

#### 2. spaCy 모델 로드 실패
```bash
python -m spacy download en_core_web_sm
```

#### 3. Node.js 버전 문제
```bash
# Node.js 18+ 필요
node --version
# 18 미만이면 업그레이드
```

#### 4. 포트 충돌
```bash
# 다른 포트 사용
python -m uvicorn main:app --reload --port 8001
npm run dev -- --port 3001
```

### 키워드 추출 테스트
```bash
cd ai-engine/preprocessing
python keyword_extractor.py
```

## 📝 개발 가이드

### 새로운 기능 추가
1. `backend/services/` 에 비즈니스 로직 추가
2. `backend/api/` 에 엔드포인트 추가
3. `frontend/src/` 에 UI 컴포넌트 추가

### 코드 스타일
- Python: PEP 8 준수
- JavaScript/TypeScript: ESLint 규칙 준수
- 커밋 메시지: 한국어 사용

## 🤝 팀 협업

### 브랜치 전략
- `main`: 프로덕션 코드
- `develop`: 개발 브랜치
- `feature/*`: 기능 개발
- `hotfix/*`: 긴급 수정

### 코드 리뷰
- 모든 PR은 리뷰 후 머지
- 테스트 코드 포함 권장

## 📞 지원

문제가 발생하면:
1. 이 README의 문제 해결 섹션 확인
2. 팀 채팅방에 문의
3. GitHub Issues 생성

---

**팀 ROOMBOT** - AI 키워드 추출 시스템


