# 🚨 문제 해결 가이드

## 허깅페이스 호환성 오류 해결

### 1. 기존 패키지 제거

```bash
pip uninstall transformers sentence-transformers torch torchvision
```

### 2. 캐시 정리

```bash
pip cache purge
```

### 3. 안정적인 버전으로 재설치

```bash
# PyTorch 먼저 설치
pip install torch==2.0.1 torchvision==0.15.2

# HuggingFace 패키지들 설치
pip install transformers==4.30.2
pip install sentence-transformers==2.2.2
pip install tokenizers==0.13.3
pip install huggingface-hub==0.16.4
```

### 4. 전체 재설치 (권장)

```bash
# 가상환경 재생성
rm -rf venv
python3 -m venv venv
source venv/bin/activate

# requirements.txt로 설치
pip install -r requirements.txt
```

## 일반적인 오류 해결

### ModuleNotFoundError: No module named 'openai'

```bash
pip install openai==1.98.0
```

### ModuleNotFoundError: No module named 'psycopg2'

```bash
pip install psycopg2-binary==2.9.10
```

### KoNLPy Java 오류

```bash
# macOS
brew install openjdk@11

# Ubuntu
sudo apt-get install openjdk-11-jdk
```

### spaCy 모델 오류

```bash
python -m spacy download en_core_web_sm
```

## 환경 확인

### 설치된 패키지 확인

```bash
pip list | grep -E "(transformers|sentence-transformers|torch|openai|spacy)"
```

### 버전 호환성 테스트

```bash
python -c "
from transformers import pipeline
from sentence_transformers import SentenceTransformer
print('✅ 모든 패키지가 정상적으로 로드됩니다')
"
```

## 지원되는 버전

| 패키지                | 버전   | 호환성  |
| --------------------- | ------ | ------- |
| transformers          | 4.30.2 | ✅ 안정 |
| sentence-transformers | 2.2.2  | ✅ 안정 |
| torch                 | 2.0.1  | ✅ 안정 |
| openai                | 1.98.0 | ✅ 최신 |
| spacy                 | 3.8.7  | ✅ 안정 |

## 문제가 지속되면

1. **로그 확인**: 백엔드 서버 로그를 확인하세요
2. **환경 재설정**: 가상환경을 완전히 재생성하세요
3. **시스템 요구사항**: Python 3.8+ 필요
4. **메모리 확인**: 최소 4GB RAM 필요 (AI 모델 로딩용)
