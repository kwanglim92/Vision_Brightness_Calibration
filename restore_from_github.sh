#!/bin/bash
# GitHub에서 정상 코드 복원 스크립트 (Mac/Linux)
# 로컬 변경사항을 버리고 GitHub 버전으로 복원

echo "============================================================"
echo "Vision_Cal.py 파일 복원"
echo "============================================================"
echo ""

echo "현재 Git 상태 확인..."
git status --short

echo ""
echo "⚠️  경고: 로컬 변경사항이 모두 사라집니다!"
echo "GitHub의 최신 버전으로 파일을 복원합니다."
echo ""

read -p "계속하시겠습니까? (y/n): " confirm
if [[ ! "$confirm" =~ ^[Yy]$ ]]; then
    echo "작업을 취소했습니다."
    exit 0
fi

echo ""
echo "백업 생성 중..."
cp Vision_Cal.py "Vision_Cal_backup_$(date +%Y%m%d_%H%M%S).py"
echo "백업 파일이 생성되었습니다."

echo ""
echo "GitHub에서 최신 버전 가져오기..."
git fetch origin

echo ""
echo "Vision_Cal.py 파일 복원 중..."
git checkout origin/master -- Vision_Cal.py

if [ $? -eq 0 ]; then
    echo ""
    echo "✅ 파일이 성공적으로 복원되었습니다!"
    echo ""
    echo "복원된 파일 정보:"
    git log -1 --oneline -- Vision_Cal.py
else
    echo ""
    echo "❌ 복원 실패. 수동으로 다음 명령을 실행해보세요:"
    echo "   git checkout HEAD -- Vision_Cal.py"
fi

echo ""