#!/usr/bin/env python3
"""
체크리스트 대화상자 테스트 스크립트
GUI 환경에서 실행하여 체크리스트가 제대로 표시되는지 확인
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

class TestChecklistDialog(tk.Toplevel):
    """테스트용 체크리스트 대화상자"""
    def __init__(self, parent, checklist_items):
        super().__init__(parent)
        
        # 부모 윈도우가 표시 가능한 경우에만 transient 설정
        try:
            if parent.winfo_viewable():
                self.transient(parent)
        except:
            pass
            
        self.title("사전 준비사항 체크리스트")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 대화상자를 항상 위에 표시
        self.lift()
        self.attributes('-topmost', True)

        # 인스턴스 변수 초기화
        self.checklist_items = checklist_items
        self.check_vars = []
        self.proceed = False

        # 위젯 생성
        self._create_widgets()

        # 화면 중앙에 위치시키기
        self.update_idletasks()  # 자체 update_idletasks 호출
        window_width = 550
        window_height = 150
        
        # 스크린 크기를 직접 가져옴
        screen_width = self.winfo_screenwidth()
        screen_height = self.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # 모든 설정이 끝난 후, 모달로 만들고 포커스를 줍니다.
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="프로그램을 시작하기 전, 아래 항목들을 모두 확인해주세요.", 
                 font=("Arial", 11, "bold")).pack(pady=(0, 15))

        checklist_frame = ttk.Frame(main_frame)
        checklist_frame.pack(fill=tk.X, padx=10)

        for item_text in self.checklist_items:
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(checklist_frame, text=item_text, variable=var, 
                                command=self._check_all_selected)
            cb.pack(anchor=tk.W, pady=3)
            self.check_vars.append(var)

        self.start_button = ttk.Button(main_frame, text="프로그램 시작", 
                                      command=self._on_start, state=tk.DISABLED)
        self.start_button.pack(pady=20)

    def _check_all_selected(self):
        self.start_button.config(state=tk.NORMAL if all(var.get() for var in self.check_vars) else tk.DISABLED)

    def _on_start(self):
        self.proceed = True
        self.destroy()

    def _on_close(self):
        if messagebox.askyesno("종료 확인", "체크리스트를 완료하지 않고 프로그램을 종료하시겠습니까?"):
            self.proceed = False
            self.destroy()

def test_scenario_1():
    """시나리오 1: withdraw()로 숨긴 부모 (원본 코드)"""
    print("테스트 1: withdraw()로 완전히 숨긴 부모 윈도우")
    root = tk.Tk()
    root.withdraw()  # 완전히 숨김
    
    def show_checklist():
        checklist = TestChecklistDialog(root, ["테스트 항목 1", "테스트 항목 2"])
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

def test_scenario_2():
    """시나리오 2: 작은 크기로 숨긴 부모 (수정된 코드)"""
    print("테스트 2: 1x1 크기로 숨긴 부모 윈도우")
    root = tk.Tk()
    root.geometry('1x1+0+0')  # 매우 작게
    root.overrideredirect(True)  # 테두리 제거
    
    def show_checklist():
        checklist = TestChecklistDialog(root, ["테스트 항목 1", "테스트 항목 2"])
        root.wait_window(checklist)
        if checklist.proceed:
            print("✓ 체크리스트 완료 - 메인 앱 시작")
            root.overrideredirect(False)
            root.geometry("400x300")
            root.deiconify()
            root.title("메인 애플리케이션")
            tk.Label(root, text="메인 프로그램", font=("Arial", 20)).pack(pady=50)
        else:
            print("✗ 체크리스트 취소됨")
            root.destroy()
    
    root.after(100, show_checklist)
    root.mainloop()

def test_scenario_3():
    """시나리오 3: iconify()로 최소화한 부모"""
    print("테스트 3: iconify()로 최소화한 부모 윈도우")
    root = tk.Tk()
    root.iconify()  # 최소화
    
    def show_checklist():
        checklist = TestChecklistDialog(root, ["테스트 항목 1", "테스트 항목 2"])
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