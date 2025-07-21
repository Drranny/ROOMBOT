# ROOMBOT ai-engine/preprocessing

이 디렉토리는 ROOMBOT 프로젝트의 문장 전처리 및 SVO(주어-동사-목적어) 구조 추출을 위한 파이썬 모듈을 모아둔 곳입니다.

---
##  빠른 실행법 (Quick Start)

1. **의존성 설치**
    ```bash
    pip install -r requirements.txt
    pip install requests python-dotenv
    python -m spacy download en_core_web_sm
    ```
2. **환경 변수 설정 (ETRI API 사용 시)**
    - 프로젝트 루트 또는 본 폴더에 `.env` 파일 생성 후 아래와 같이 입력:
      ```
      ETRI_API_KEY=여기에_발급받은_키_입력
      ```
3. **테스트 실행**
    - 각 파일은 `python 파일명.py`로 단독 실행 시 테스트 코드가 동작합니다.
    ```bash
    python sentence_splitter.py
    python svo_extractor_ko.py
    python svo_extractor_en.py
    ```

---
##  주요 파일 및 역할

- **sentence_splitter.py**
  - 텍스트를 문장 단위로 분리합니다.
  - 구조화된 JSON으로 변환하는 함수 제공

- **svo_extractor.py**
  - 언어별 SVO 추출 통합 진입점
  - `analyze_svo(text, lang, api_key=None)` 함수 제공 (lang: 'ko' 또는 'en')

- **svo_extractor_ko.py**
  - 한국어 SVO(주어-동사-목적어) 추출
  - ETRI 의미역 분석 API 활용 (API 키 필요, 환경변수 `ETRI_API_KEY`)
  - 구어체/문어체 모두 지원, 폴백 처리 내장

- **svo_extractor_en.py**
  - 영어 SVO 추출 (spaCy 엔진 사용, 모델: `en_core_web_sm`)

---



## 💡 간단 사용 예시

```python
from sentence_splitter import split_sentences, to_structured_json
from svo_extractor import analyze_svo

text = "세종대왕은 1392년에 조선을 건국했다. 세종대왕의 아버지는 태조 이성계이다."
print(split_sentences(text))
print(to_structured_json(text))

# SVO 추출 (한국어)
svo_ko = analyze_svo(text, lang="ko", api_key="<ETRI_API_KEY>")
print(svo_ko)

# SVO 추출 (영어)
text_en = "John and Mary eat an apple and a banana. The book was read by Tom."
svo_en = analyze_svo(text_en, lang="en")
print(svo_en)
```

---

## 참고
- 각 파일의 `__main__` 블록에서 테스트 코드 제공
- ETRI API 키는 환경변수 또는 직접 인자로 전달 가능

