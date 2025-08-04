#!/bin/bash

echo "🔍 ROOMBOT 환경 진단을 시작합니다..."
echo "=================================="

# Python 버전 확인
echo "🐍 Python 버전 확인..."
python3 --version
if [ $? -eq 0 ]; then
    echo "✅ Python 설치됨"
else
    echo "❌ Python이 설치되지 않았습니다."
fi

# Java 버전 확인 (konlpy용)
echo ""
echo "☕ Java 버전 확인..."
java -version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Java 설치됨"
else
    echo "❌ Java가 설치되지 않았습니다. konlpy 사용을 위해 Java 8-11을 설치해주세요."
fi

# Node.js 버전 확인
echo ""
echo "📦 Node.js 버전 확인..."
node --version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Node.js 설치됨"
else
    echo "❌ Node.js가 설치되지 않았습니다."
fi

# npm 확인
echo ""
echo "📦 npm 확인..."
npm --version 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ npm 설치됨"
else
    echo "❌ npm이 설치되지 않았습니다."
fi

# 가상환경 확인
echo ""
echo "🔧 Python 가상환경 확인..."
if [ -d "venv" ]; then
    echo "✅ 가상환경 폴더 존재"
else
    echo "⚠️  가상환경이 생성되지 않았습니다."
fi

# requirements.txt 확인
echo ""
echo "📋 requirements.txt 확인..."
if [ -f "requirements.txt" ]; then
    echo "✅ requirements.txt 존재"
else
    echo "❌ requirements.txt가 없습니다."
fi

# .env 파일 확인
echo ""
echo "🔐 환경 변수 파일 확인..."
if [ -f ".env" ]; then
    echo "✅ .env 파일 존재"
else
    echo "⚠️  .env 파일이 없습니다. env.example을 복사하여 생성해주세요."
fi

# spaCy 모델 확인
echo ""
echo "🌐 spaCy 영어 모델 확인..."
python3 -c "import spacy; nlp = spacy.load('en_core_web_sm'); print('✅ spaCy 영어 모델 로드 성공')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ spaCy 영어 모델 설치됨"
else
    echo "❌ spaCy 영어 모델이 설치되지 않았습니다."
    echo "💡 다음 명령어를 실행해주세요: python -m spacy download en_core_web_sm"
fi

# openpyxl 확인
echo ""
echo "📊 openpyxl 확인..."
python3 -c "import openpyxl; print('✅ openpyxl 설치됨')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ openpyxl 설치됨"
else
    echo "❌ openpyxl이 설치되지 않았습니다."
    echo "💡 다음 명령어를 실행해주세요: pip install openpyxl"
fi

# konlpy 태거 확인
echo ""
echo "🇰🇷 konlpy 태거 확인..."
python3 -c "from konlpy.tag import Okt; okt = Okt(); print('✅ Okt 태거 초기화 성공')" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ konlpy 태거 사용 가능"
else
    echo "❌ konlpy 태거 초기화 실패"
    echo "💡 Java 설치를 확인해주세요: brew install openjdk@11"
fi

# HuggingFace 모델 확인
echo ""
echo "🤗 HuggingFace 모델 확인..."
python3 -c "
try:
    from transformers import pipeline
    from sentence_transformers import SentenceTransformer
    print('✅ HuggingFace 모델 로드 성공')
except Exception as e:
    print(f'❌ HuggingFace 모델 로드 실패: {e}')
" 2>/dev/null

echo ""
echo "=================================="
echo "🎯 환경 진단 완료!"
echo ""
echo "📝 다음 단계:"
echo "   1. 문제가 있다면 위의 해결 방법을 따라주세요"
echo "   2. 모든 것이 정상이면 ./scripts/install.sh 실행"
echo "   3. 설치 완료 후 ./scripts/dev.sh로 개발 서버 실행"
