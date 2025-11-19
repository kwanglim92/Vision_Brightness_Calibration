"""
개선된 체크리스트 다이얼로그 테스트 스크립트
"""

import tkinter as tk
from src.gui.checklist_dialog import ChecklistDialog


def test_checklist_dialog():
    """체크리스트 다이얼로그 테스트"""
    # 루트 윈도우 생성
    root = tk.Tk()
    root.withdraw()  # 루트 윈도우 숨기기

    # 체크리스트 카테고리 정의
    checklist_categories = {
        "① 사전 완료 테스트": [
            "White balance 설정 완료",
            "Vimba Viewer 설정 완료",
        ],
        "② Camera Vision Setting": [
            "Brightness: 50 설정 확인",
            "Contrast: 0 설정 확인",
            "Light Strength: 50 설정 확인"
        ],
        "③ Sample Focus Setting": [
            "Tip-Sample Distance: 1.0mm 설정",
            "측정 Sample: Bare Si 준비"
        ],
        "④ Capture Image 저장": [
            "Vision Mode: Large 선택",
            "Capture: Displayed 설정",
            "이미지 측정 및 저장 완료"
        ],
    }

    # 체크리스트 다이얼로그 표시
    dialog = ChecklistDialog(root, checklist_categories)
    root.wait_window(dialog)

    # 결과 출력
    if dialog.proceed:
        print("✓ 체크리스트 완료 - 프로그램 시작")
    else:
        print("✗ 체크리스트 취소 - 프로그램 종료")

    root.destroy()


if __name__ == "__main__":
    print("=" * 60)
    print("개선된 체크리스트 다이얼로그 테스트")
    print("=" * 60)
    print("\n테스트 항목:")
    print("  1. 진행률 표시 (프로그레스 바 및 퍼센트)")
    print("  2. 카테고리별 상태 표시 (아이콘 및 색상)")
    print("  3. 체크된 항목 스타일 변경 (회색 텍스트)")
    print("  4. 중요 항목 강조 (빨간색 텍스트)")
    print("  5. 툴팁 표시 (마우스 오버)")
    print("  6. 버튼 동적 텍스트 (남은 항목 표시)")
    print("  7. 레이아웃 및 여백 개선")
    print("\n다이얼로그를 열고 있습니다...")
    print("-" * 60)

    test_checklist_dialog()

    print("-" * 60)
    print("테스트 완료!")
    print("=" * 60)
