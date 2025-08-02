#!/bin/bash

echo "🔧 ROOMBOT 환경 변수 설정을 도와드립니다..."
echo "=" * 50

# .env 파일이 이미 존재하는지 확인
if [ -f ".env" ]; then
    echo "⚠️  .env 파일이 이미 존재합니다."
    read -p "덮어쓰시겠습니까? (y/N): " overwrite
    if [[ $overwrite != "y" && $overwrite != "Y" ]]; then
        echo "설정을 취소했습니다."
        exit 0
    fi
fi

# env.example을 .env로 복사
cp env.example .env

echo "✅ .env 파일이 생성되었습니다."
echo ""
echo "📝 다음 단계를 따라주세요:"
echo ""
echo "🔑 1. .env 파일을 편집하여 OpenAI API 키를 입력하세요:"
echo "   # 이 줄의 주석을 해제하고 실제 API 키를 입력하세요"
echo "   # OPENAI_API_KEY=sk-your-actual-api-key-here"
echo "   OPENAI_API_KEY=sk-여기에_실제_API_키_입력"
echo ""
echo "🌐 2. OpenAI API 키가 없다면 다음에서 발급받으세요:"
echo "   https://platform.openai.com/api-keys"
echo ""
echo "3. Firebase 인증을 사용하려면 주석 처리된 Firebase 설정을 활성화하세요"
echo ""
echo "💡 편집기로 .env 파일을 열려면:"
echo "   code .env  # VS Code"
echo "   nano .env  # 터미널 편집기"
echo "   vim .env   # Vim 편집기"

# .env 파일을 편집할지 묻기
read -p "지금 .env 파일을 편집하시겠습니까? (y/N): " edit_now
if [[ $edit_now == "y" || $edit_now == "Y" ]]; then
    if command -v code &> /dev/null; then
        code .env
    elif command -v nano &> /dev/null; then
        nano .env
    elif command -v vim &> /dev/null; then
        vim .env
    else
        echo "편집기를 찾을 수 없습니다. 수동으로 .env 파일을 편집해주세요."
    fi
fi

echo ""
echo "🎯 환경 변수 설정이 완료되었습니다!"
echo "이제 ./scripts/install.sh를 실행하여 설치를 진행하세요." 