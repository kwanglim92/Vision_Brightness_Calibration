"""
ChecklistDialog 모듈
프로그램 시작 전 사전 준비사항을 확인하는 모달 대화상자
버전 1.3.0: UI/UX 개선 (진행률 표시, 시각적 피드백, 툴팁)
"""

import tkinter as tk
from tkinter import messagebox, ttk


# 색상 상수 정의
COLORS = {
    'success': '#4CAF50',       # 초록 - 완료
    'warning': '#FFA500',       # 주황 - 진행중 (50-99%)
    'danger': '#FF4444',        # 빨강 - 미완료/중요 (0-50%)
    'info': '#2196F3',          # 파랑 - 진행중 카테고리
    'neutral': '#CCCCCC',       # 회색 - 기본
    'text_completed': '#888888',    # 회색 - 완료된 텍스트
    'text_important': '#D32F2F',    # 짙은 빨강 - 중요 항목
    'bg_tooltip': '#FFFFCC',    # 연한 노랑 - 툴팁 배경
}


class ToolTip:
    """위젯에 툴팁을 추가하는 클래스"""

    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        self.widget.bind("<Enter>", self.show_tooltip)
        self.widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        """툴팁 표시"""
        if self.tooltip_window or not self.text:
            return

        # 위젯의 위치 계산
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 5

        # 툴팁 윈도우 생성
        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        # 툴팁 레이블
        label = tk.Label(tw, text=self.text,
                        background=COLORS['bg_tooltip'],
                        foreground='black',
                        relief="solid",
                        borderwidth=1,
                        font=("Arial", 9),
                        padx=8,
                        pady=5,
                        wraplength=400)
        label.pack()

    def hide_tooltip(self, event=None):
        """툴팁 숨기기"""
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None


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

        # 새로운 인스턴스 변수
        self.total_items = 0          # 전체 항목 수
        self.checked_items = 0        # 체크된 항목 수
        self.progress_label = None    # 진행률 레이블
        self.progress_bar = None      # 진행률 바
        self.category_frames = {}     # 카테고리 프레임 참조
        self.tooltips_data = {}       # 툴팁 데이터

        # 스타일 설정
        self._configure_styles()

        # 툴팁 데이터 초기화
        self._initialize_tooltips()

        # 위젯 생성
        self._create_widgets()

        # 화면 중앙에 위치시키기
        self.update_idletasks()  # 자체 update_idletasks 호출
        window_width = 850
        window_height = 680

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
        main_frame = ttk.Frame(self, padding=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # 제목
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(title_frame, text="Vision의 밝기 측정 및 Calibration 조건",
                 font=("Arial", 13, "bold")).pack()
        ttk.Label(title_frame, text="※ White balance 및 vimba setting 완료 상태",
                 font=("Arial", 10, "italic"), foreground="red").pack(pady=(5, 0))

        # 진행률 표시 프레임
        progress_frame = ttk.Frame(main_frame)
        progress_frame.pack(fill=tk.X, pady=(5, 10))

        # 진행률 레이블
        self.progress_label = ttk.Label(progress_frame,
                                       text="완료: 0/0 항목 (0%)",
                                       font=("Arial", 10, "bold"))
        self.progress_label.pack(pady=(0, 5))

        # 진행률 바
        self.progress_bar = ttk.Progressbar(progress_frame,
                                           length=810,
                                           mode='determinate',
                                           maximum=100)
        self.progress_bar.pack(fill=tk.X)

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
            # 전체 항목 수 계산
            self.total_items += len(items)

            # 카테고리 프레임 (초기 상태: NotStarted)
            category_title = f"○ {category} [0/{len(items)}]"
            category_frame = ttk.LabelFrame(scrollable_frame, text=category_title,
                                           padding=10, style='NotStarted.TLabelframe')
            category_frame.pack(fill=tk.X, padx=10, pady=8)

            # 카테고리 프레임 참조 저장
            self.category_frames[category] = category_frame

            # 카테고리 내 항목들
            self.check_vars[category] = []
            for item_text in items:
                var = tk.BooleanVar(value=False)

                # 중요 항목 확인
                is_important = any(keyword in item_text
                                 for keyword in ["White balance", "Vimba Viewer"])

                # 체크박스 생성
                cb = ttk.Checkbutton(category_frame, text=item_text,
                                    variable=var,
                                    style='Important.TCheckbutton' if is_important else 'TCheckbutton',
                                    command=lambda c=category: self._on_check_changed(c))
                cb.pack(anchor=tk.W, pady=3, padx=15)

                # 툴팁 추가
                tooltip_text = self.tooltips_data.get(item_text, "")
                if tooltip_text:
                    ToolTip(cb, tooltip_text)

                # 체크박스와 변수 저장
                self.check_vars[category].append((var, cb))

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
        remaining_text = f"남은 항목: {self.total_items}개" if self.total_items > 0 else ""
        button_text = f"프로그램 시작 ({remaining_text})" if remaining_text else "프로그램 시작"
        self.start_button = ttk.Button(button_container, text=button_text,
                                      command=self._on_start,
                                      style='Start.TButton',
                                      state=tk.DISABLED, width=42)
        self.start_button.grid(row=1, column=0, columnspan=2, padx=8, pady=(5, 10))

        # 초기 진행률 업데이트
        self._update_progress()

    def _on_check_changed(self, category):
        """체크박스 상태 변경 시 호출"""
        # 카테고리 상태 업데이트
        self._update_category_status(category)

        # 전체 진행률 업데이트
        self._update_progress()

        # 체크된 항목 스타일 변경
        self._update_checkbox_styles(category)

        # 시작 버튼 활성화 체크
        self._check_all_selected()

    def _check_all_selected(self):
        """모든 항목이 선택되었는지 확인하고 시작 버튼 활성화"""
        all_checked = all(
            all(var.get() for var, _ in vars_list)
            for vars_list in self.check_vars.values()
        )

        if all_checked:
            self.start_button.config(state=tk.NORMAL, text="✓ 프로그램 시작")
        else:
            remaining = self.total_items - self.checked_items
            self.start_button.config(
                state=tk.DISABLED,
                text=f"프로그램 시작 (남은 항목: {remaining}개)"
            )

    def _select_all(self):
        """모든 체크박스 선택"""
        for category, vars_list in self.check_vars.items():
            for var, _ in vars_list:
                var.set(True)
            self._update_category_status(category)
            self._update_checkbox_styles(category)
        self._update_progress()
        self._check_all_selected()

    def _clear_all(self):
        """모든 체크박스 해제"""
        for category, vars_list in self.check_vars.items():
            for var, _ in vars_list:
                var.set(False)
            self._update_category_status(category)
            self._update_checkbox_styles(category)
        self._update_progress()
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

    def _configure_styles(self):
        """커스텀 스타일 설정"""
        style = ttk.Style()

        # LabelFrame 스타일 - 카테고리별 상태 표시
        style.configure('Completed.TLabelframe',
                        foreground=COLORS['success'])
        style.configure('Completed.TLabelframe.Label',
                        foreground=COLORS['success'],
                        font=('Arial', 10, 'bold'))

        style.configure('InProgress.TLabelframe',
                        foreground=COLORS['info'])
        style.configure('InProgress.TLabelframe.Label',
                        foreground=COLORS['info'],
                        font=('Arial', 10, 'bold'))

        style.configure('NotStarted.TLabelframe',
                        foreground=COLORS['neutral'])
        style.configure('NotStarted.TLabelframe.Label',
                        foreground=COLORS['neutral'],
                        font=('Arial', 10))

        # 버튼 스타일 - 시작 버튼 강조
        style.configure('Start.TButton',
                        font=('Arial', 11, 'bold'),
                        padding=10)

        # Checkbutton 스타일
        style.configure('Completed.TCheckbutton',
                        foreground=COLORS['text_completed'])
        style.configure('Important.TCheckbutton',
                        foreground=COLORS['text_important'])

    def _initialize_tooltips(self):
        """툴팁 데이터 초기화"""
        self.tooltips_data = {
            "White balance 설정 완료": "Vimba Viewer에서 White Balance 자동 조정 후 설정값 확인",
            "Vimba Viewer 설정 완료": "Exposure Time 및 Gain 값이 적절하게 설정되었는지 확인",
            "Brightness: 50 설정 확인": "XE Software의 Vision 설정에서 Brightness를 50으로 설정",
            "Contrast: 0 설정 확인": "XE Software의 Vision 설정에서 Contrast를 0으로 설정",
            "Light Strength: 50 설정 확인": "XE Software의 Vision 설정에서 Light Strength를 50으로 설정",
            "Tip-Sample Distance: 1.0mm 설정": "접근 모드에서 팁-샘플 간격을 정확히 1.0mm로 설정",
            "측정 Sample: Bare Si 준비": "표준 실리콘 웨이퍼 샘플을 스테이지에 장착",
            "Vision Mode: Large 선택": "Vision 모드를 Large로 선택하여 전체 영역 확인",
            "Capture: Displayed 설정": "현재 화면에 표시된 이미지를 캡처하도록 설정",
            "이미지 측정 및 저장 완료": "캡처한 이미지를 지정된 폴더에 저장"
        }

    def _update_progress(self):
        """전체 진행률 업데이트"""
        # 체크된 항목 수 계산
        self.checked_items = sum(
            sum(1 for var, _ in vars_list if var.get())
            for vars_list in self.check_vars.values()
        )

        # 퍼센트 계산
        percentage = int((self.checked_items / self.total_items) * 100) if self.total_items > 0 else 0

        # 레이블 업데이트
        self.progress_label.config(
            text=f"완료: {self.checked_items}/{self.total_items} 항목 ({percentage}%)"
        )

        # 프로그레스 바 업데이트
        self.progress_bar['value'] = percentage

        # 프로그레스 바 색상 변경
        self._update_progress_color(percentage)

    def _update_progress_color(self, percentage):
        """진행률에 따라 프로그레스 바 색상 변경"""
        style = ttk.Style()

        if percentage == 100:
            # 완료: 초록색
            style.configure("TProgressbar", foreground=COLORS['success'],
                          background=COLORS['success'])
        elif percentage >= 51:
            # 진행중 (51-99%): 주황색
            style.configure("TProgressbar", foreground=COLORS['warning'],
                          background=COLORS['warning'])
        else:
            # 미완료 (0-50%): 빨간색
            style.configure("TProgressbar", foreground=COLORS['danger'],
                          background=COLORS['danger'])

    def _update_category_status(self, category):
        """특정 카테고리의 상태 업데이트"""
        vars_list = self.check_vars[category]
        checked = sum(1 for var, _ in vars_list if var.get())
        total = len(vars_list)

        # 상태 아이콘 결정
        if checked == total:
            status = "✓"
            style = 'Completed.TLabelframe'
        elif checked > 0:
            status = "⚠"
            style = 'InProgress.TLabelframe'
        else:
            status = "○"
            style = 'NotStarted.TLabelframe'

        # 카테고리 프레임 업데이트
        frame = self.category_frames[category]
        # 원본 카테고리명 추출 (아이콘 제거)
        original_category = category
        for prefix in ["○ ", "⚠ ", "✓ "]:
            if category.startswith(prefix):
                original_category = category[2:]
                break

        new_title = f"{status} {original_category} [{checked}/{total}]"
        frame.configure(text=new_title, style=style)

    def _update_checkbox_styles(self, category):
        """카테고리 내 체크박스 스타일 업데이트"""
        vars_list = self.check_vars[category]

        for var, cb in vars_list:
            if var.get():
                # 체크된 항목: 회색 텍스트
                cb.configure(foreground=COLORS['text_completed'])
            else:
                # 중요 항목 확인
                item_text = cb.cget('text')
                is_important = any(keyword in item_text
                                 for keyword in ["White balance", "Vimba Viewer"])

                if is_important:
                    cb.configure(foreground=COLORS['text_important'])
                else:
                    cb.configure(foreground='black')
