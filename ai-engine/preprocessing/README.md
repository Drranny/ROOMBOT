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
    python test_predicate_extraction.py
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
  - **서술어(predicate) 추출 기능 추가**: 동사(VV), 형용사(VA), 보조동사(VX) 모두 처리
  - ETRI 의미역 분석 API 활용 (API 키 필요, 환경변수 `ETRI_API_KEY`)
  - 구어체/문어체 모두 지원, 폴백 처리 내장

- **svo_extractor_konlpy.py**
  - **KoNLPy 기반 한국어 SVO 추출** (ETRI API 대안)
  - Okt, Komoran, Hannanum 태거 지원
  - API 키 불필요, 로컬에서 실행
  - 빠른 처리 속도, 안정적인 성능

- **svo_extractor_en.py**
  - 영어 SVO 추출 (spaCy 엔진 사용, 모델: `en_core_web_sm`)
  - **서술어(predicate) 추출 기능 추가**: 동사(VERB), 형용사(ADJ), 보조동사(AUX) 모두 처리

- **test_predicate_extraction.py**
  - 서술어 추출 기능 테스트 스크립트
  - 한국어/영어 서술어 추출 비교 테스트
  - ETRI API와 KoNLPy 성능 비교

---

## 🆕 서술어(Predicate) 추출 기능

### 개선 사항
- **기존**: 주어(S), 동사(V), 목적어(O)만 추출
- **개선**: 서술어 타입을 구분하여 추출 (동사, 형용사, 보조동사 등)
- **목적어 없는 문장 처리**: 자동사, 형용사 서술어 등 목적어가 없는 문장도 올바르게 처리

### 한국어 서술어 타입
- `VV`: 동사 (예: 읽다, 먹다, 가다)
- `VA`: 형용사 (예: 좋다, 아름답다, 맛있다)
- `VX`: 보조동사 (예: 있다, 없다)

### 영어 서술어 타입
- `VERB`: 동사 (예: eat, read, go)
- `ADJ`: 형용사 (예: beautiful, happy, delicious)
- `AUX`: 보조동사 (예: is, are, have)

### 문장 구조별 처리
1. **타동사 문장** (목적어 있음)
   - "학생이 책을 읽는다." → S: 학생, V: 읽다, O: 책, has_object: true

2. **자동사 문장** (목적어 없음)
   - "아이가 놀았다." → S: 아이, V: 놀다, O: 없음, has_object: false

3. **형용사 서술어 문장** (목적어 없음)
   - "날씨가 좋다." → S: 날씨, V: 좋다, O: 없음, has_object: false

4. **서술격 조사 문장** (목적어 없음)
   - "그는 학생이다." → S: 그는, V: 이다, O: 없음, has_object: false

### 사용 예시
```python
from svo_extractor import analyze_svo

# 한국어 형용사 서술어 (목적어 없음) - ETRI API 사용
text_ko = "날씨가 좋다."
result_ko = analyze_svo(text_ko, lang="ko", api_key="<ETRI_API_KEY>")
print(result_ko['svo']['predicate_type'])  # 'VA' (형용사)
print(result_ko['svo']['has_object'])      # False (목적어 없음)

# 한국어 형용사 서술어 (목적어 없음) - KoNLPy 사용
result_ko_konlpy = analyze_svo(text_ko, lang="ko", method="konlpy")
print(result_ko_konlpy['svo']['predicate_type'])  # 'VA' (형용사)
print(result_ko_konlpy['svo']['has_object'])      # False (목적어 없음)

# 영어 형용사 서술어 (목적어 없음)
text_en = "The weather is beautiful."
result_en = analyze_svo(text_en, lang="en")
print(result_en['svo']['predicate_type'])  # 'ADJ' (형용사)
print(result_en['svo']['has_object'])      # False (목적어 없음)
```

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
- 서술어 추출 기능은 형태소 분석과 의미역 분석을 결합하여 정확도를 향상시킴

