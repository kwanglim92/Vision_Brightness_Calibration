#!/usr/bin/env python3
"""
개선된 체크리스트 대화상자 테스트
카테고리별로 구성된 체크리스트 확인
"""

import tkinter as tk
from tkinter import ttk, messagebox
import sys

class ImprovedChecklistDialog(tk.Toplevel):
    """개선된 체크리스트 대화상자"""
    def __init__(self, parent, checklist_categories):
        super().__init__(parent)
        
        # 부모 윈도우가 표시 가능한 경우에만 transient 설정
        try:
            if parent.winfo_viewable():
                self.transient(parent)
        except:
            pass
            
        self.title("XEA Camera Vision & Safety - 사전 준비사항 체크리스트")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)
        
        # 대화상자를 항상 위에 표시
        self.lift()
        self.attributes('-topmost', True)

        # 인스턴스 변수 초기화
        self.checklist_categories = checklist_categories
        self.check_vars = {}
        self.proceed = False

        # 위젯 생성
        self._create_widgets()

        # 화면 중앙에 위치시키기
        self.update_idletasks()
        window_width = 700
        window_height = 550
        
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

        # 제목
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text="Vision의 밝기 측정 및 Calibration 조건", 
                 font=("Arial", 13, "bold")).pack()
        ttk.Label(title_frame, text="※ White balance 및 vimba setting 완료 상태", 
                 font=("Arial", 10, "italic"), foreground="red").pack(pady=(5, 0))

        # 스크롤 가능한 체크리스트 영역
        canvas = tk.Canvas(main_frame, height=350)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # 카테고리별 체크리스트 생성
        for category, items in self.checklist_categories.items():
            # 카테고리 프레임
            category_frame = ttk.LabelFrame(scrollable_frame, text=category, 
                                           padding=10)
            category_frame.pack(fill=tk.X, padx=10, pady=5)
            
            # 카테고리 내 항목들
            self.check_vars[category] = []
            for item_text in items:
                var = tk.BooleanVar(value=False)
                cb = ttk.Checkbutton(category_frame, text=item_text, 
                                    variable=var, 
                                    command=self._check_all_selected)
                cb.pack(anchor=tk.W, pady=2, padx=10)
                self.check_vars[category].append(var)
        
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        
        # 버튼 프레임
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))
        
        # 전체 선택/해제 버튼
        self.select_all_btn = ttk.Button(button_frame, text="전체 선택", 
                                         command=self._select_all, width=12)
        self.select_all_btn.pack(side=tk.LEFT, padx=5)
        
        self.clear_all_btn = ttk.Button(button_frame, text="전체 해제", 
                                        command=self._clear_all, width=12)
        self.clear_all_btn.pack(side=tk.LEFT, padx=5)
        
        # 프로그램 시작 버튼
        self.start_button = ttk.Button(button_frame, text="프로그램 시작", 
                                      command=self._on_start, 
                                      state=tk.DISABLED, width=15)
        self.start_button.pack(side=tk.RIGHT, padx=5)

    def _check_all_selected(self):
        all_checked = all(
            all(var.get() for var in vars_list) 
            for vars_list in self.check_vars.values()
        )
        self.start_button.config(state=tk.NORMAL if all_checked else tk.DISABLED)
    
    def _select_all(self):
        """모든 체크박스 선택"""
        for vars_list in self.check_vars.values():
            for var in vars_list:
                var.set(True)
        self._check_all_selected()
    
    def _clear_all(self):
        """모든 체크박스 해제"""
        for vars_list in self.check_vars.values():
            for var in vars_list:
                var.set(False)
        self._check_all_selected()

    def _on_start(self):
        self.proceed = True
        self.destroy()

    def _on_close(self):
        if messagebox.askyesno("종료 확인", "체크리스트를 완료하지 않고 프로그램을 종료하시겠습니까?"):
            self.proceed = False
            self.destroy()

def test_new_checklist():
    """새로운 체크리스트 테스트"""
    print("개선된 체크리스트 대화상자 테스트")
    print("=" * 60)
    
    root = tk.Tk()
    root.geometry('1x1+0+0')
    root.overrideredirect(True)
    
    def show_checklist():
        # 실제 사용될 체크리스트 카테고리
        checklist_categories = {
            "① Camera Vision Setting": [
                "Brightness: 50 설정 확인",
                "Contrast: 0 설정 확인",
                "Light Strength: 50 설정 확인"
            ],
            "② Sample Focus Setting": [
                "Tip-Sample Distance: 1.0mm 설정",
                "측정 Sample: Bare Si 준비"
            ],
            "③ Capture Image 저장": [
                "Vision Mode: Large 선택",
                "Capture: Displayed 설정",
                "이미지 측정 및 저장 완료"
            ],
            "④ 사전 완료 테스트": [
                "White balance 설정 완료",
                "Vimba Viewer 설정 완료",
                "Camera 연결 상태 확인"
            ]
        }
        
        checklist = ImprovedChecklistDialog(root, checklist_categories)
        root.wait_window(checklist)
        
        if checklist.proceed:
            print("✓ 모든 체크리스트 완료 - 프로그램 시작")
            
            # 메인 프로그램 시뮬레이션
            root.overrideredirect(False)
            root.geometry("600x400")
            root.deiconify()
            root.title("Vision Brightness Calibration")
            
            main_frame = ttk.Frame(root, padding=20)
            main_frame.pack(fill=tk.BOTH, expand=True)
            
            ttk.Label(main_frame, text="Vision Brightness Calibration", 
                     font=("Arial", 20, "bold")).pack(pady=20)
            ttk.Label(main_frame, text="체크리스트 완료!\n프로그램이 정상적으로 시작되었습니다.", 
                     font=("Arial", 12)).pack(pady=10)
            
            # 체크된 항목들 표시
            result_frame = ttk.LabelFrame(main_frame, text="완료된 체크리스트", padding=10)
            result_frame.pack(fill=tk.BOTH, expand=True, pady=10)
            
            result_text = tk.Text(result_frame, height=10, width=50)
            result_text.pack()
            
            for category, items in checklist_categories.items():
                result_text.insert(tk.END, f"\n{category}:\n")
                for item in items:
                    result_text.insert(tk.END, f"  ✓ {item}\n")
            
            result_text.config(state=tk.DISABLED)
            
            ttk.Button(main_frame, text="종료", command=root.destroy).pack(pady=10)
        else:
            print("✗ 체크리스트 취소됨")
            root.destroy()
    
    root.after(100, show_checklist)
    root.mainloop()

def main():
    print("=" * 60)
    print("개선된 체크리스트 대화상자 테스트")
    print("=" * 60)
    print("\n카테고리별 체크리스트:")
    print("1. Camera Vision Setting")
    print("2. Sample Focus Setting")
    print("3. Capture Image 저장")
    print("4. 사전 완료 테스트")
    print("\n기능:")
    print("- 전체 선택/해제 버튼")
    print("- 카테고리별 구분")
    print("- 스크롤 가능한 체크리스트")
    print("=" * 60)
    
    try:
        test_new_checklist()
    except Exception as e:
        print(f"오류 발생: {e}")

if __name__ == "__main__":
    # GUI 환경 확인
    try:
        import os
        if not os.environ.get('DISPLAY') and sys.platform != 'win32':
            print("⚠️  경고: GUI 환경이 아닙니다.")
            print("Windows, Mac 또는 Linux 데스크톱에서 실행해주세요.")
    except:
        pass
    
    main()