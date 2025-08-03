#!/bin/bash

echo "🚀 ROOMBOT 개발 서버 시작..."
echo "================================"

# 백엔드 서버 시작
echo "🔧 백엔드 서버 시작 중..."
cd backend
source ../venv/bin/activate && uvicorn main:app --reload --host 0.0.0.0 --port 8000 &
BACKEND_PID=$!
cd ..

# 잠시 대기
sleep 3

# 프론트엔드 서버 시작
echo "🎨 프론트엔드 서버 시작 중..."
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..

echo ""
echo "✅ 서버들이 시작되었습니다!"
echo "📱 백엔드: http://localhost:8000"
echo "🌐 프론트엔드: http://localhost:3000"
echo ""
echo "서버를 중지하려면 Ctrl+C를 누르세요."

# 프로세스 종료 처리
trap "echo '서버를 종료합니다...'; kill $BACKEND_PID $FRONTEND_PID; exit" INT

# 대기
wait 