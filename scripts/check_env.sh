#!/bin/bash

echo "🔍 ROOMBOT 개발 환경 진단 시작..."
echo "=================================="

# Python 버전 확인
echo "📦 Python 환경 확인:"
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python 설치됨"
else
    echo "❌ Python 설치 필요"
    exit 1
fi

# Node.js 버전 확인
echo ""
echo "📦 Node.js 환경 확인:"
node --version
if [ $? -eq 0 ]; then
    echo "✅ Node.js 설치됨"
else
    echo "❌ Node.js 설치 필요"
    exit 1
fi

# npm 버전 확인
npm --version
if [ $? -eq 0 ]; then
    echo "✅ npm 설치됨"
else
    echo "❌ npm 설치 필요"
    exit 1
fi

# 가상환경 확인
echo ""
echo "🐍 Python 가상환경 확인:"
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "✅ 가상환경 활성화됨: $VIRTUAL_ENV"
else
    echo "⚠️  가상환경이 활성화되지 않았습니다."
    echo "   source venv/bin/activate 실행 권장"
fi

# Python 패키지 확인
echo ""
echo "📦 Python 패키지 확인:"
REQUIRED_PACKAGES=("fastapi" "uvicorn" "sqlalchemy" "psycopg2" "openai" "spacy" "konlpy" "firebase_admin")
for package in "${REQUIRED_PACKAGES[@]}"; do
    if python3 -c "import $package" 2>/dev/null; then
        echo "✅ $package 설치됨"
    else
        echo "❌ $package 설치 필요"
    fi
done

# spaCy 모델 확인
echo ""
echo "🤖 spaCy 모델 확인:"
if python3 -c "import spacy; spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "✅ spaCy 영어 모델 설치됨"
else
    echo "❌ spaCy 영어 모델 설치 필요: python -m spacy download en_core_web_sm"
fi

# Java 확인 (KoNLPy 필요)
echo ""
echo "☕ Java 환경 확인:"
java -version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Java 설치됨"
else
    echo "❌ Java 설치 필요 (KoNLPy용)"
fi

# 환경변수 확인
echo ""
echo "🔧 환경변수 확인:"
if [ -n "$OPENAI_API_KEY" ]; then
    echo "✅ OPENAI_API_KEY 설정됨"
else
    echo "⚠️  OPENAI_API_KEY 설정 필요"
fi

if [ -n "$POSTGRES_URL" ]; then
    echo "✅ POSTGRES_URL 설정됨"
else
    echo "⚠️  POSTGRES_URL 설정 필요"
fi

echo ""
echo "🎉 환경 진단 완료!"
echo "문제가 있다면 ./scripts/install.sh를 실행하세요." 