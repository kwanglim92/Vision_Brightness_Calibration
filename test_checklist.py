#!/usr/bin/env python3
"""
체크리스트 대화상자 테스트 스크립트
GUI 환경에서 실행하여 체크리스트가 제대로 표시되는지 확인
"""

import tkinter as tk
import sys

# ChecklistDialog를 별도 모듈에서 import
from src.gui.checklist_dialog import ChecklistDialog


def run_test_scenario(parent_setup_func, scenario_name):
    """공통 테스트 시나리오 실행 함수"""
    print(f"테스트: {scenario_name}")
    root = tk.Tk()
    parent_setup_func(root)  # 부모 윈도우 설정

    def show_checklist():
        # 간단한 테스트 체크리스트
        test_checklist = {
            "테스트 항목": [
                "테스트 항목 1",
                "테스트 항목 2"
            ]
        }

        checklist = ChecklistDialog(root, test_checklist)
        root.wait_window(checklist)

        if checklist.proceed:
            print("✓ 체크리스트 완료 - 메인 앱 시작")
            root.deiconify()
            root.geometry("400x300")
            root.title("메인 애플리케이션")
            tk.Label(root, text="메인 프로그램", font=("Arial", 20)).pack(pady=50)
        else:
            print("✗ 체크리스트 취소됨")
            root.destroy()

    root.after(100, show_checklist)
    root.mainloop()


def test_scenario_1():
    """시나리오 1: withdraw()로 숨긴 부모 (원본 코드)"""
    run_test_scenario(
        lambda root: root.withdraw(),
        "withdraw()로 완전히 숨긴 부모 윈도우"
    )


def test_scenario_2():
    """시나리오 2: 작은 크기로 숨긴 부모 (수정된 코드)"""
    def setup(root):
        root.geometry('1x1+0+0')
        root.overrideredirect(True)

    run_test_scenario(setup, "1x1 크기로 숨긴 부모 윈도우 (권장)")


def test_scenario_3():
    """시나리오 3: iconify()로 최소화한 부모"""
    run_test_scenario(
        lambda root: root.iconify(),
        "iconify()로 최소화한 부모 윈도우"
    )

def main():
    print("=" * 60)
    print("체크리스트 대화상자 테스트")
    print("=" * 60)
    print("\n어떤 시나리오를 테스트하시겠습니까?")
    print("1. withdraw() - 원본 코드 (문제 있음)")
    print("2. 1x1 크기 - 수정된 코드 (권장)")
    print("3. iconify() - 대안")
    print("q. 종료")
    
    while True:
        choice = input("\n선택 (1/2/3/q): ").strip()
        
        if choice == '1':
            test_scenario_1()
            break
        elif choice == '2':
            test_scenario_2()
            break
        elif choice == '3':
            test_scenario_3()
            break
        elif choice.lower() == 'q':
            print("테스트를 종료합니다.")
            break
        else:
            print("잘못된 선택입니다. 다시 입력해주세요.")

if __name__ == "__main__":
    # GUI 환경 확인
    try:
        import os
        if not os.environ.get('DISPLAY'):
            print("⚠️  경고: DISPLAY 환경변수가 설정되지 않았습니다.")
            print("GUI 환경에서 실행해주세요.")
            sys.exit(1)
    except:
        pass
    
    main()