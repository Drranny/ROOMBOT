#!/bin/bash

echo "🚀 ROOMBOT 개발 환경 설치를 시작합니다..."

# 1. Python 가상환경 확인 및 생성
echo "📦 Python 가상환경을 확인합니다..."
if [ -d "venv" ]; then
    echo "✅ 가상환경이 이미 존재합니다."
    read -p "기존 가상환경을 사용하시겠습니까? (Y/n): " use_existing
    if [[ $use_existing != "n" && $use_existing != "N" ]]; then
        echo "기존 가상환경을 사용합니다."
    else
        echo "기존 가상환경을 삭제하고 새로 생성합니다..."
        rm -rf venv
        python3 -m venv venv
    fi
else
    echo "📦 Python 가상환경을 생성합니다..."
    python3 -m venv venv
fi

# 가상환경 활성화
source venv/bin/activate

# 2. Python 의존성 설치 (이미 설치된 경우 확인)
echo "📦 Python 패키지들을 확인합니다..."
if pip list | grep -q "fastapi"; then
    echo "✅ Python 패키지들이 이미 설치되어 있습니다."
    read -p "패키지를 다시 설치하시겠습니까? (y/N): " reinstall
    if [[ $reinstall == "y" || $reinstall == "Y" ]]; then
        echo "📦 Python 패키지들을 설치합니다..."
        pip install --upgrade pip
        pip install -r requirements.txt
    else
        echo "기존 패키지를 사용합니다."
    fi
else
    echo "📦 Python 패키지들을 설치합니다..."
    pip install --upgrade pip
    pip install -r requirements.txt
fi

# 3. spaCy 영어 모델 확인 및 설치
echo "🌐 spaCy 영어 모델을 확인합니다..."
if python -c "import spacy; nlp = spacy.load('en_core_web_sm')" 2>/dev/null; then
    echo "✅ spaCy 영어 모델이 이미 설치되어 있습니다."
else
    echo "🌐 spaCy 영어 모델을 설치합니다..."
    python -m spacy download en_core_web_sm
fi

# 4. Java 의존성 확인 (konlpy용)
echo "☕ Java 의존성을 확인합니다..."
if command -v java &> /dev/null; then
    echo "✅ Java가 설치되어 있습니다."
else
    echo "⚠️  Java가 설치되지 않았습니다. konlpy 사용을 위해 Java를 설치해주세요."
    echo "   macOS: brew install openjdk@11"
    echo "   Ubuntu: sudo apt-get install openjdk-11-jdk"
fi

# 5. Node.js 의존성 확인 및 설치
echo "📦 Node.js 패키지들을 확인합니다..."
if [ -d "frontend/node_modules" ]; then
    echo "✅ Node.js 패키지들이 이미 설치되어 있습니다."
    read -p "패키지를 다시 설치하시겠습니까? (y/N): " reinstall_npm
    if [[ $reinstall_npm == "y" || $reinstall_npm == "Y" ]]; then
        echo "📦 Node.js 패키지들을 설치합니다..."
        cd frontend
        npm install
        cd ..
    else
        echo "기존 Node.js 패키지를 사용합니다."
    fi
else
    echo "📦 Node.js 패키지들을 설치합니다..."
    cd frontend
    npm install
    cd ..
fi

echo "✅ 설치가 완료되었습니다!"
echo ""
echo "🎯 다음 명령어로 개발 서버를 실행하세요:"
echo "   Backend: cd backend && python -m uvicorn main:app --reload"
echo "   Frontend: cd frontend && npm run dev"
echo "   또는: ./scripts/dev.sh (한 번에 실행)"
