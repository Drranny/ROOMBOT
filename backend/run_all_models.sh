#!/bin/bash

# SBERT 모델 서버들을 동시에 실행하는 스크립트

# 스크립트가 있는 디렉토리로 이동
cd "$(dirname "$0")"

echo "🤖 SBERT 모델 서버들을 시작합니다..."
echo "=================================="

# 기존 서버들 종료
echo "기존 서버들을 종료합니다..."
pkill -f "uvicorn.*api.*8000"
pkill -f "uvicorn.*api.*8001"
pkill -f "uvicorn.*api.*8002"
pkill -f "uvicorn.*api.*8003"
sleep 2

# 서버들 백그라운드에서 실행
echo "1. paraphrase-multilingual-MiniLM-L12-v2 서버 시작 (포트 8000)..."
uvicorn api:app --reload --host 0.0.0.0 --port 8000 > logs/server_8000.log 2>&1 &
SERVER_8000_PID=$!

echo "2. paraphrase-mpnet-base-v2 서버 시작 (포트 8001)..."
uvicorn api_mpnet:app --reload --host 0.0.0.0 --port 8001 > logs/server_8001.log 2>&1 &
SERVER_8001_PID=$!

echo "3. paraphrase-multilingual-mpnet-base-v2 서버 시작 (포트 8002)..."
uvicorn api_multilingual_mpnet:app --reload --host 0.0.0.0 --port 8002 > logs/server_8002.log 2>&1 &
SERVER_8002_PID=$!

echo "4. sentence-t5-base 서버 시작 (포트 8003)..."
uvicorn api_t5:app --reload --host 0.0.0.0 --port 8003 > logs/server_8003.log 2>&1 &
SERVER_8003_PID=$!

# 로그 디렉토리 생성
mkdir -p logs

# 서버 시작 대기
echo "서버들이 시작되는 동안 잠시 기다립니다..."
sleep 10

# 서버 상태 확인
echo ""
echo "📊 서버 상태 확인:"
echo "=================="

check_server() {
    local port=$1
    local model_name=$2
    if curl -s http://localhost:$port/health > /dev/null 2>&1; then
        echo "✅ 포트 $port ($model_name): 정상"
    else
        echo "❌ 포트 $port ($model_name): 연결 실패"
    fi
}

check_server 8000 "paraphrase-multilingual-MiniLM-L12-v2"
check_server 8001 "paraphrase-mpnet-base-v2"
check_server 8002 "paraphrase-multilingual-mpnet-base-v2"
check_server 8003 "sentence-t5-base"

echo ""
echo "🌐 API 문서 링크:"
echo "=================="
echo "포트 8000: http://localhost:8000/docs"
echo "포트 8001: http://localhost:8001/docs"
echo "포트 8002: http://localhost:8002/docs"
echo "포트 8003: http://localhost:8003/docs"

echo ""
echo "🧪 테스트 실행:"
echo "==============="
echo "python test_models.py"

echo ""
echo "📝 로그 파일:"
echo "============="
echo "포트 8000: logs/server_8000.log"
echo "포트 8001: logs/server_8001.log"
echo "포트 8002: logs/server_8002.log"
echo "포트 8003: logs/server_8003.log"

echo ""
echo "🛑 서버 종료하려면:"
echo "=================="
echo "pkill -f 'uvicorn.*api'"

# PID 저장
echo $SERVER_8000_PID > logs/server_8000.pid
echo $SERVER_8001_PID > logs/server_8001.pid
echo $SERVER_8002_PID > logs/server_8002.pid
echo $SERVER_8003_PID > logs/server_8003.pid

echo ""
echo "�� 모든 서버가 시작되었습니다!" 