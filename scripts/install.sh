#!/bin/bash

echo "🚀 ROOMBOT 설치를 시작합니다..."
echo "=================================="

# Python 가상환경 생성
echo "🐍 Python 가상환경을 생성합니다..."
python3 -m venv venv
source venv/bin/activate

# pip 업그레이드
echo "📦 pip를 최신 버전으로 업그레이드합니다..."
pip install --upgrade pip

# PyTorch 먼저 설치 (호환성 문제 방지)
echo "🔥 PyTorch를 먼저 설치합니다..."
pip install torch==2.0.1 torchvision==0.15.2

# 기본 의존성 설치
echo "📦 기본 의존성을 설치합니다..."
pip install -r requirements.txt

# spaCy 영어 모델 설치
echo "🌐 spaCy 영어 모델을 설치합니다..."
python -m spacy download en_core_web_sm

# NLTK 데이터 다운로드
echo "📚 NLTK 데이터를 다운로드합니다..."
python -c "import nltk; nltk.download('wordnet'); nltk.download('omw-1.4')"

# HuggingFace 모델 테스트
echo "🤗 HuggingFace 모델을 테스트합니다..."
python -c "
try:
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    print('✅ HuggingFace 모델 로드 성공')
except Exception as e:
    print(f'⚠️  HuggingFace 모델 로드 실패: {e}')
    print('💡 버전 호환성 문제일 수 있습니다. requirements.txt를 확인해주세요.')
"

# KoNLPy 테스트 (Java 필요)
echo "🇰🇷 KoNLPy를 테스트합니다..."
python -c "
try:
    from konlpy.tag import Okt
    okt = Okt()
    print('✅ KoNLPy 설치 성공')
except Exception as e:
    print(f'⚠️  KoNLPy 초기화 실패: {e}')
    print('💡 Java 8-11을 설치해주세요: brew install openjdk@11')
"

# 환경 변수 파일 생성
echo "🔐 환경 변수 파일을 생성합니다..."
if [ ! -f ".env" ]; then
    cp env.example .env 2>/dev/null || echo "OPENAI_API_KEY=your_openai_api_key_here" > .env
    echo "✅ .env 파일이 생성되었습니다. OPENAI_API_KEY를 설정해주세요."
else
    echo "✅ .env 파일이 이미 존재합니다."
fi

echo ""
echo "🎉 설치가 완료되었습니다!"
echo ""
echo "📝 다음 단계:"
echo "   1. .env 파일에서 OPENAI_API_KEY를 설정하세요"
echo "   2. ./scripts/dev.sh로 개발 서버를 실행하세요"
echo "   3. http://localhost:3000에서 애플리케이션을 확인하세요"
echo ""
echo "🔧 문제가 있다면 ./scripts/check_env.sh를 실행해보세요"
echo ""
echo "⚠️  허깅페이스 호환성 문제가 발생하면:"
echo "   pip uninstall transformers sentence-transformers torch"
echo "   pip install -r requirements.txt"
