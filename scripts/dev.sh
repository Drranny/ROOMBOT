#!/bin/bash

echo "🚀 ROOMBOT 개발 서버를 시작합니다..."

# 가상환경 활성화
if [ -d "venv" ]; then
    echo "🔧 가상환경을 활성화합니다..."
    source venv/bin/activate
    PYTHON_PATH="$(which python)"
    echo "✅ Python 경로: $PYTHON_PATH"
else
    echo "❌ 가상환경이 없습니다. 먼저 ./scripts/install.sh를 실행해주세요."
    exit 1
fi

# 백그라운드에서 백엔드 실행
echo "🔧 백엔드 서버를 시작합니다..."
cd backend
$PYTHON_PATH -m uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 잠시 대기
sleep 3

# 백그라운드에서 프론트엔드 실행
echo "🎨 프론트엔드 서버를 시작합니다..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo "✅ 서버가 시작되었습니다!"
echo ""
echo "🌐 접속 주소:"
echo "   Frontend: http://localhost:3000"
echo "   Backend API: http://localhost:8000"
echo "   API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 서버를 중지하려면 Ctrl+C를 누르세요"

# 프로세스 종료 함수
cleanup() {
    echo ""
    echo "🛑 서버를 종료합니다..."
    kill $BACKEND_PID 2>/dev/null
    kill $FRONTEND_PID 2>/dev/null
    exit 0
}

# Ctrl+C 시그널 처리
trap cleanup SIGINT

# 프로세스가 실행 중인 동안 대기
wait 