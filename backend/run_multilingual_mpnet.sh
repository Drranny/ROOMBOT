#!/bin/bash

# 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

echo "🚀 paraphrase-multilingual-mpnet-base-v2 모델 서버를 시작합니다..."
echo "=============================================================="

# 기존 서버 종료
pkill -f "uvicorn.*api_multilingual_mpnet.*8002"
sleep 2

# 서버 실행
echo "포트 8002에서 서버를 시작합니다..."
uvicorn api_multilingual_mpnet:app --reload --host 0.0.0.0 --port 8002

echo ""
echo "🌐 API 문서: http://localhost:8002/docs"
echo "🛑 서버 종료: Ctrl+C" 