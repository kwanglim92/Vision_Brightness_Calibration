"""
ChecklistDialog 모듈
프로그램 시작 전 사전 준비사항을 확인하는 모달 대화상자
"""

import tkinter as tk
from tkinter import messagebox, ttk


class ChecklistDialog(tk.Toplevel):
    """프로그램 시작 전 사전 준비사항을 확인하는 모달 대화상자"""

    def __init__(self, parent, checklist_categories):
        super().__init__(parent)

        # 부모 윈도우가 표시 가능한 경우에만 transient 설정
        try:
            if parent.winfo_viewable():
                self.transient(parent)
        except:
            pass

        self.title("Vision Brightness Calibration")
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
        self.update_idletasks()  # 자체 update_idletasks 호출
        window_width = 800
        window_height = 620

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
        """대화상자의 위젯들을 생성"""
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
        button_frame.pack(fill=tk.X, pady=(15, 5))

        # 버튼 컨테이너 (중앙 정렬용)
        button_container = ttk.Frame(button_frame)
        button_container.pack(anchor=tk.CENTER)

        # 첫 번째 줄: 전체 선택, 전체 해제
        self.select_all_btn = ttk.Button(button_container, text="전체 선택",
                                         command=self._select_all, width=20)
        self.select_all_btn.grid(row=0, column=0, padx=8, pady=5)

        self.clear_all_btn = ttk.Button(button_container, text="전체 해제",
                                        command=self._clear_all, width=20)
        self.clear_all_btn.grid(row=0, column=1, padx=8, pady=5)

        # 두 번째 줄: 프로그램 시작 (중앙)
        self.start_button = ttk.Button(button_container, text="프로그램 시작",
                                      command=self._on_start,
                                      state=tk.DISABLED, width=42)
        self.start_button.grid(row=1, column=0, columnspan=2, padx=8, pady=(5, 10))

    def _check_all_selected(self):
        """모든 항목이 선택되었는지 확인하고 시작 버튼 활성화"""
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
        """프로그램 시작 버튼 클릭 시"""
        self.proceed = True
        self.destroy()

    def _on_close(self):
        """창 닫기 시"""
        # 대화상자를 최상위로 올리고 포커스 설정
        self.lift()
        self.focus_force()

        if messagebox.askyesno("종료 확인", "체크리스트를 완료하지 않고 프로그램을 종료하시겠습니까?", parent=self):
            self.proceed = False
            self.destroy()
