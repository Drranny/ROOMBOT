# SBERT Sentence Similarity API

여러 SBERT 모델을 사용한 문장 유사도 계산 API 서버들입니다.

## 지원하는 모델

1. **paraphrase-multilingual-MiniLM-L12-v2** (포트 8000) - 다국어 지원, 빠른 처리
2. **paraphrase-mpnet-base-v2** (포트 8001) - 높은 정확도, 영어에 특화
3. **paraphrase-multilingual-mpnet-base-v2** (포트 8002) - 다국어 지원, 높은 정확도
4. **sentence-t5-base** (포트 8003) - T5 기반, sentence-t5-large도 지원

## 서버 실행 방법

### 모든 서버 동시 실행

```bash
./run_all_models.sh
```

### 개별 서버 실행

```bash
# paraphrase-mpnet-base-v2 서버
./run_mpnet.sh

# paraphrase-multilingual-mpnet-base-v2 서버
./run_multilingual_mpnet.sh

# sentence-t5-base 서버
./run_t5.sh

# 기존 multilingual-minilm 서버
uvicorn api:app --reload --host 0.0.0.0 --port 8000
```

## API 엔드포인트

각 서버는 다음 엔드포인트를 제공합니다:

- `GET /` - API 정보
- `POST /similarity` - 두 문장 간 유사도 계산
- `POST /batch-similarity` - 여러 문장 쌍의 유사도 일괄 계산
- `POST /find-similar` - 쿼리 문장과 가장 유사한 문장들 찾기
- `GET /health` - 서버 상태 확인

## API 문서

- 포트 8000: http://localhost:8000/docs
- 포트 8001: http://localhost:8001/docs
- 포트 8002: http://localhost:8002/docs
- 포트 8003: http://localhost:8003/docs

## 모델 비교 테스트

```bash
python test_models.py
```

이 스크립트는 모든 서버에 대해 동일한 테스트를 실행하고 결과를 비교합니다.

## 예제 요청

### 단일 유사도 계산

```bash
curl -X POST "http://localhost:8001/similarity" \
     -H "Content-Type: application/json" \
     -d '{
       "sentence1": "안녕하세요",
       "sentence2": "Hello"
     }'
```

### 배치 유사도 계산

```bash
curl -X POST "http://localhost:8002/batch-similarity" \
     -H "Content-Type: application/json" \
     -d '{
       "sentence_pairs": [
         ["안녕하세요", "Hello"],
         ["오늘 날씨가 좋네요", "The weather is nice today"]
       ]
     }'
```

### 유사한 문장 찾기

```bash
curl -X POST "http://localhost:8003/find-similar" \
     -H "Content-Type: application/json" \
     -d '{
       "query_sentence": "안녕하세요",
       "candidate_sentences": ["안녕", "반갑습니다", "Hello", "Good morning"],
       "top_k": 3
     }'
```

## 모델별 특징

### paraphrase-multilingual-MiniLM-L12-v2

- **장점**: 빠른 처리 속도, 다국어 지원, 메모리 효율적
- **단점**: 정확도가 상대적으로 낮을 수 있음
- **용도**: 실시간 처리, 대량 데이터 처리

### paraphrase-mpnet-base-v2

- **장점**: 높은 정확도, 영어에 특화
- **단점**: 처리 속도가 상대적으로 느림, 영어에만 특화
- **용도**: 정확도가 중요한 영어 텍스트 처리

### paraphrase-multilingual-mpnet-base-v2

- **장점**: 높은 정확도, 다국어 지원
- **단점**: 처리 속도가 상대적으로 느림, 메모리 사용량 많음
- **용도**: 정확도가 중요한 다국어 텍스트 처리

### sentence-t5-base/large

- **장점**: T5 기반으로 강력한 언어 이해 능력
- **단점**: 모델 크기가 큼, 처리 속도 느림
- **용도**: 복잡한 언어 이해가 필요한 경우

## 서버 종료

```bash
# 모든 서버 종료
pkill -f 'uvicorn.*api'

# 특정 포트 서버만 종료
pkill -f 'uvicorn.*8001'
```

## 로그 확인

```bash
# 모든 로그 확인
tail -f logs/server_*.log

# 특정 서버 로그 확인
tail -f logs/server_8001.log
```
