 🤖 ROOMBOT: AI 환각 탐지기 (역사·과학·스포츠 특화)

> 생성형 AI가 만든 문장, 진짜일까 거짓일까?  
ROOMBOT은 GPT가 생성한 문장을 외부 정보와 비교 분석해
> 사실/부분사실/환각 여부를 판별하고, 그 결과를 시각화 + 리포트로 제공

---

## 📌 주요 기능

- ✅ GPT 응답 자동 수집 (질문 입력 → 응답 출력)
- ✅ 의미 단위(SVO) 문장 구조화
- ✅ Google/Wiki 기반 외부 정보 검색
- ✅ SBERT 유사도 분석 → 환각 판단 (사실/부분사실/환각)
- ✅ 문장별 결과 시각화 (색상/차트)
- ✅ 환각률 요약 리포트 PDF/CSV 다운로드

---

## 🎯 분석 대상 주제

| 주제             | 이유                                                               |
|------------------|--------------------------------------------------------------------|
| 🏛️ 한국 역사      | 연도/인물/사건 오류 많음, 위키 기반 검증 쉬움                           |
| 🔬 과학 발명 & 노벨상 | 발명 시점·수상 연도 착오 자주 발생, 공식 목록으로 검증 가능                |
| 🏅 스포츠 메달 기록   | 연도/선수/종목 오류 잦음, Wikipedia/Google로 빠른 검증 가능             |

---

## ⚙️ 기술 스택

| 분야       | 사용 기술                                                            |
|------------|---------------------------------------------------------------------|
| **Frontend** | Next.js, TailwindCSS, Chart.js                                    |
| **Backend**  | FastAPI, Pydantic, PostgreSQL                                     |
| **AI/NLP**   | KoNLPy, spaCy, Sentence-BERT, OpenAI GPT API                      |
| **외부 검색** | Google Custom Search API, Wikipedia API, Nobel API 등             |

---

## 📁 폴더 구조


ai-hallucination-detector/
├── frontend/        # Next.js 프론트엔드
├── backend/         # FastAPI 백엔드
├── ai-engine/       # 문장 분석, SBERT, 환각 판단 로직
├── data/            # 예시 질문/응답 및 테스트 세트
├── docs/            # 기획 문서, 역할 분담, 플로우 설명
├── scripts/         # 실행 및 배포 자동화 스크립트
├── .vscode/         # VSCode 설정
├── .gitignore
├── README.md
└── .env.example


🚀 실행 방법
1️⃣ 클론 & 환경설정


git clone https://github.com/Drranny/ROOMBOT.git
cd ROOMBOT
cp .env.example .env
-� .env 파일에 OpenAI API 키, Google API 키 등 입력

2️⃣ 프론트엔드 실행


cd frontend
npm install
npm run dev
http://localhost:3000 에서 실행 확인

3️⃣ 백엔드 실행

cd backend
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
http://localhost:8000/docs 로 Swagger 열람 가능

 예시 화면
입력	GPT 응답	환각 탐지 결과
"세종대왕은 1392년에 조선을 세웠다"	❌ 환각	유사도 0.31 → 환각으로 분류됨

👥 팀 역할
이름	역할	주요 작업
윤정	GPT 응답 처리, 의미 분석	GPT API 연동, 문장 SVO 추출
지유	서버/DB, 검색 API	FastAPI, Wiki/Google 검색
재석	유사도 판단, 시각화	SBERT 분석, 차트 구성, 리포트 다운로드


