import cv2
import numpy as np
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
from PIL import Image, ImageTk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure
import pandas as pd
import os
from datetime import datetime
import xml.etree.ElementTree as ET
import webbrowser

class ChecklistDialog(tk.Toplevel):
    """프로그램 시작 전 사전 준비사항을 확인하는 모달 대화상자"""
    def __init__(self, parent, checklist_items):
        super().__init__(parent)
        self.transient(parent) # 부모-자식 관계 설정

        self.title("사전 준비사항 체크리스트")
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", self._on_close)

        # 인스턴스 변수 초기화
        self.checklist_items = checklist_items
        self.check_vars = []
        self.proceed = False

        # 위젯 생성
        self._create_widgets()

        # 화면 중앙에 위치시키기 (부모 창이 숨겨져 있을 때를 대비해 update_idletasks 호출)
        parent.update_idletasks()
        window_width = 550
        window_height = 150
        screen_width = parent.winfo_screenwidth()
        screen_height = parent.winfo_screenheight()
        x_coordinate = (screen_width // 2) - (window_width // 2)
        y_coordinate = (screen_height // 2) - (window_height // 2)
        self.geometry(f"{window_width}x{window_height}+{x_coordinate}+{y_coordinate}")

        # 모든 설정이 끝난 후, 모달로 만들고 포커스를 줍니다.
        self.grab_set()
        self.focus_set()

    def _create_widgets(self):
        main_frame = ttk.Frame(self, padding=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(main_frame, text="프로그램을 시작하기 전, 아래 항목들을 모두 확인해주세요.", font=("Arial", 11, "bold")).pack(pady=(0, 15))

        checklist_frame = ttk.Frame(main_frame)
        checklist_frame.pack(fill=tk.X, padx=10)

        for item_text in self.checklist_items: # 이제 self.checklist_items를 사용
            var = tk.BooleanVar(value=False)
            cb = ttk.Checkbutton(checklist_frame, text=item_text, variable=var, command=self._check_all_selected)
            cb.pack(anchor=tk.W, pady=3)
            self.check_vars.append(var)

        self.start_button = ttk.Button(main_frame, text="프로그램 시작", command=self._on_start, state=tk.DISABLED)
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

class 명도측정프로그램:
    # --- 상수 정의 ---
    TARGET_BRIGHTNESS = 128
    KEY_LSG = "LightStrengthGain"
    PRESET_MANUAL = "직접 선택"
    PRESET_STANDARD = "기준 영역 (70,100)-(400,300)"
    XML_TAG_ITEM = ".//Item"
    XML_TAG_NAME = "Name"
    XML_TAG_VALUE = "Value"
    XML_TAG_PART = ".//Part"
    XML_TAG_TYPE = "Type"
    XML_TYPE_CAMERA = "Camera"

    def __init__(self, root):
        self.root = root
        self.root.title("Vision Brightness Calibration (v1.1.0)")
        # 더 큰 창 크기로 설정
        self.root.geometry("1200x750")

        # 메뉴 바 추가 (도움말 메뉴만) - 임시로 주석 처리
        self.create_menu_bar()

        # 변수 초기화
        self.image = None
        self.pil_image = None
        self.tk_image = None
        self.selection_rect = None
        self.start_x, self.start_y, self.end_x, self.end_y = 0, 0, 0, 0
        self.is_selecting = False
        self.scale_factor = 1.0
        self.current_avg_brightness = 0
        self.is_full_image_analysis = False
        self.max_image_width = 600  # 최대 이미지 표시 너비
        self.max_image_height = 500  # 최대 이미지 표시 높이

        # 측정 기록 관리용 변수 추가
        self.measurements = []
        self.measurement_columns = ["날짜시간", "이미지명", "영역", "평균명도", "RGB평균", "LightStrengthGain", "권장조정값"]

        # 줌 팩터 변수
        self.zoom_factor = 1.0

        # DB 파일 경로 설정
        self.db_file_path = ""
        self.has_setup_db_path = False
        self.db_lsg_keyword = ""
        self.db_separator = ""

        # 원본 DB 값 저장 변수
        self.original_db_values = { self.KEY_LSG: 1.0 }

        # UI 생성 및 이벤트 바인딩
        self._setup_ui()
        self._bind_events()

        # 초기 히스토그램 그리기
        self.init_histogram()

    def _setup_ui(self):
        """UI 레이아웃과 위젯들을 생성합니다."""
        # 메인 프레임 생성
        self.main_frame = ttk.Frame(self.root)
        self.main_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # 좌측과 우측 패널 생성
        self._create_left_panel()
        self._create_right_panel()

    def _create_left_panel(self):
        """이미지, 컨트롤 버튼, 히스토그램을 포함하는 좌측 패널을 생성합니다."""
        self.left_frame = ttk.Frame(self.main_frame)
        self.left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # --- 이미지 캔버스 ---
        self.canvas_container = ttk.Frame(self.left_frame, width=self.max_image_width, height=self.max_image_height)
        self.canvas_container.pack(side=tk.TOP, fill=tk.BOTH, expand=True, pady=5)
        self.canvas_container.pack_propagate(False)

        canvas_frame = ttk.Frame(self.canvas_container)
        canvas_frame.pack(fill=tk.BOTH, expand=True)

        self.canvas_x_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.HORIZONTAL)
        self.canvas_y_scrollbar = ttk.Scrollbar(canvas_frame, orient=tk.VERTICAL)
        self.canvas = tk.Canvas(canvas_frame, bg="lightgray",
                                xscrollcommand=self.canvas_x_scrollbar.set,
                                yscrollcommand=self.canvas_y_scrollbar.set)
        self.canvas_x_scrollbar.config(command=self.canvas.xview)
        self.canvas_y_scrollbar.config(command=self.canvas.yview)
        self.canvas_y_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.canvas.pack(side=tk.TOP, fill=tk.BOTH, expand=True)
        self.canvas_x_scrollbar.pack(side=tk.BOTTOM, fill=tk.X)

        # --- 컨트롤 버튼 ---
        button_frame = ttk.Frame(self.left_frame)
        button_frame.pack(fill=tk.X, pady=5)

        self.load_btn = ttk.Button(button_frame, text="이미지 불러오기", command=self.load_image)
        self.load_btn.pack(side=tk.LEFT, padx=5)

        preset_frame = ttk.Frame(button_frame)
        preset_frame.pack(side=tk.LEFT, padx=5)
        ttk.Label(preset_frame, text="선택 영역:").pack(side=tk.LEFT, padx=(0, 5))
        self.preset_var = tk.StringVar()
        self.preset_combo = ttk.Combobox(preset_frame, textvariable=self.preset_var,
                                         values=[self.PRESET_MANUAL, self.PRESET_STANDARD],
                                         width=25, state="readonly")
        self.preset_combo.current(0)
        self.preset_combo.pack(side=tk.LEFT)

        self.reset_btn = ttk.Button(button_frame, text="선택 영역 초기화", command=self.reset_selection)
        self.reset_btn.pack(side=tk.LEFT, padx=5)
        self.full_image_btn = ttk.Button(button_frame, text="전체 이미지 분석", command=self.analyze_full_image)
        self.full_image_btn.pack(side=tk.LEFT, padx=5)

        zoom_frame = ttk.Frame(button_frame)
        zoom_frame.pack(side=tk.RIGHT, padx=5)
        self.zoom_in_btn = ttk.Button(zoom_frame, text="확대 (+)", command=self.zoom_in, width=8)
        self.zoom_in_btn.pack(side=tk.LEFT, padx=2)
        self.zoom_out_btn = ttk.Button(zoom_frame, text="축소 (-)", command=self.zoom_out, width=8)
        self.zoom_out_btn.pack(side=tk.LEFT, padx=2)
        self.zoom_reset_btn = ttk.Button(zoom_frame, text="원본 크기", command=self.zoom_reset, width=8)
        self.zoom_reset_btn.pack(side=tk.LEFT, padx=2)

        # --- 히스토그램 ---
        self.hist_frame = ttk.LabelFrame(self.left_frame, text="히스토그램")
        self.hist_frame.pack(fill=tk.X, pady=5, ipady=5)
        plt.rcParams['font.family'] = 'Malgun Gothic'
        plt.rcParams['axes.unicode_minus'] = False
        self.fig = Figure(figsize=(6, 2), dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.1, bottom=0.2, right=0.95, top=0.9)
        self.canvas_hist = FigureCanvasTkAgg(self.fig, master=self.hist_frame)
        self.canvas_hist.get_tk_widget().pack(fill=tk.BOTH, expand=True, padx=5, pady=5)

    def _create_right_panel(self):
        """결과, DB 설정, 기록을 포함하는 우측 패널을 생성합니다."""
        self.right_frame = ttk.Frame(self.main_frame, width=500)
        self.right_frame.pack(side=tk.RIGHT, fill=tk.BOTH, padx=(10, 0))
        self.right_frame.pack_propagate(False)

        # --- 측정 결과 ---
        result_frame_container = ttk.Frame(self.right_frame)
        result_frame_container.pack(fill=tk.X, pady=5)

        self.result_frame = ttk.LabelFrame(result_frame_container, text="측정 결과")
        self.result_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.result_frame, text="선택 영역:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.region_label = ttk.Label(self.result_frame, text="-")
        self.region_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.result_frame, text="평균 명도:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.brightness_label = ttk.Label(self.result_frame, text="-", font=("Arial", 12, "bold"), foreground="blue")
        self.brightness_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.result_frame, text="표준편차:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.std_label = ttk.Label(self.result_frame, text="-")
        self.std_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.result_frame, text="최소/최대 명도:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.min_max_label = ttk.Label(self.result_frame, text="-")
        self.min_max_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.result_frame, text="평균 RGB:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
        self.rgb_label = ttk.Label(self.result_frame, text="-")
        self.rgb_label.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)

        self.full_image_frame = ttk.LabelFrame(result_frame_container, text="전체 이미지 정보")
        self.full_image_frame.pack(fill=tk.X, pady=2)
        ttk.Label(self.full_image_frame, text="이미지 크기:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=2)
        self.image_size_label = ttk.Label(self.full_image_frame, text="-")
        self.image_size_label.grid(row=0, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.full_image_frame, text="전체 평균 명도:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=2)
        self.full_brightness_label = ttk.Label(self.full_image_frame, text="-", font=("Arial", 12, "bold"), foreground="blue")
        self.full_brightness_label.grid(row=1, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.full_image_frame, text="전체 표준편차:").grid(row=2, column=0, sticky=tk.W, padx=5, pady=2)
        self.full_std_label = ttk.Label(self.full_image_frame, text="-")
        self.full_std_label.grid(row=2, column=1, sticky=tk.W, padx=5, pady=2)
        ttk.Label(self.full_image_frame, text="평균 RGB:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
        self.full_rgb_label = ttk.Label(self.full_image_frame, text="-")
        self.full_rgb_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)

        # --- DB 설정 ---
        self.db_frame = ttk.LabelFrame(self.right_frame, text="DB 설정")
        self.db_frame.pack(fill=tk.X, pady=5)
        vcmd = (self.root.register(self.validate_float_input), '%P')

        ttk.Label(self.db_frame, text="LightStrengthGain:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        light_strength_frame = ttk.Frame(self.db_frame)
        light_strength_frame.grid(row=0, column=1, padx=5, pady=5, sticky=tk.W)
        self.light_strength_var = tk.DoubleVar(value=1.0)
        self.light_strength_scale = ttk.Scale(light_strength_frame, from_=0.0, to=1.0, variable=self.light_strength_var, orient=tk.HORIZONTAL, length=180, command=self.update_light_strength)
        self.light_strength_scale.pack(side=tk.LEFT)
        self.light_strength_entry = ttk.Entry(light_strength_frame, width=7, textvariable=self.light_strength_var, validate='key', validatecommand=vcmd)
        self.light_strength_entry.pack(side=tk.LEFT, padx=5)
        self.reset_lsg_btn = ttk.Button(light_strength_frame, text="초기화", command=lambda: self.reset_db_value(self.KEY_LSG), width=6)
        self.reset_lsg_btn.pack(side=tk.LEFT, padx=5)

        db_button_frame = ttk.Frame(self.db_frame)
        db_button_frame.grid(row=1, column=0, columnspan=2, pady=5)
        self.reset_all_db_btn = ttk.Button(db_button_frame, text="DB 값 불러오기", command=self.load_db_values, width=12)
        self.reset_all_db_btn.pack(side=tk.LEFT, padx=5)
        self.db_apply_btn = ttk.Button(db_button_frame, text="DB 즉시 적용", command=self.apply_db_to_file, width=10)
        self.db_apply_btn.pack(side=tk.LEFT, padx=5)

        # --- 권장 조정값 ---
        self.recommend_frame = ttk.LabelFrame(self.right_frame, text="권장 조정값")
        self.recommend_frame.pack(fill=tk.X, pady=5)
        self.recommend_text = tk.Text(self.recommend_frame, wrap=tk.WORD, height=7, width=50)
        self.recommend_text.pack(pady=5, padx=5, fill=tk.X, expand=True)
        self.recommend_text.config(state=tk.DISABLED)
        self.recommend_text.tag_configure("header", font=("Arial", 11, "bold"), foreground="darkblue")
        self.recommend_text.tag_configure("normal", font=("Arial", 10))
        self.recommend_text.tag_configure("value", font=("Arial", 11, "bold"), foreground="red")
        self.recommend_text.tag_configure("arrow", font=("Arial", 11), foreground="blue")

        # 재계산 버튼 프레임
        recalc_frame = ttk.Frame(self.recommend_frame)
        recalc_frame.pack(fill=tk.X, padx=5, pady=(0, 5))
        self.recalc_btn = ttk.Button(recalc_frame, text="현재 DB 값으로 권장값 재계산", command=self.recalculate_recommendations)
        self.recalc_btn.pack(side=tk.RIGHT)

        # --- 측정 기록 ---
        self.history_frame = ttk.LabelFrame(self.right_frame, text="측정 기록")
        self.history_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        history_listbox_frame = ttk.Frame(self.history_frame)
        history_listbox_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=2)
        self.history_listbox = tk.Listbox(history_listbox_frame, height=6)
        self.history_listbox.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        history_scrollbar = ttk.Scrollbar(history_listbox_frame, orient=tk.VERTICAL, command=self.history_listbox.yview)
        history_scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        self.history_listbox.config(yscrollcommand=history_scrollbar.set)

        history_button_frame = ttk.Frame(self.history_frame)
        history_button_frame.pack(fill=tk.X, pady=5)
        self.clear_history_btn = ttk.Button(history_button_frame, text="측정 기록 초기화", command=self.clear_measurement_history, width=16)
        self.clear_history_btn.pack(side=tk.LEFT, padx=3)
        self.save_btn = ttk.Button(history_button_frame, text="측정 결과 저장", command=self.save_measurement, width=12)
        self.save_btn.pack(side=tk.LEFT, padx=3)
        self.export_btn = ttk.Button(history_button_frame, text="Excel로 내보내기", command=self.export_to_excel, width=14)
        self.export_btn.pack(side=tk.LEFT, padx=3)
        self.report_btn = ttk.Button(history_button_frame, text="보고서 생성", command=self.generate_report, width=10)
        self.report_btn.pack(side=tk.LEFT, padx=3)

    def _bind_events(self):
        """UI 위젯에 대한 이벤트 핸들러를 바인딩합니다."""
        # 캔버스 마우스 이벤트
        self.canvas.bind("<ButtonPress-1>", self.on_mouse_down)
        self.canvas.bind("<B1-Motion>", self.on_mouse_move)
        self.canvas.bind("<ButtonRelease-1>", self.on_mouse_up)

        # 프리셋 콤보박스 이벤트
        self.preset_combo.bind('<<ComboboxSelected>>', self.on_preset_selected)

        # 기록 리스트박스 선택 이벤트
        self.history_listbox.bind("<<ListboxSelect>>", self.on_history_select)

        # 마우스 휠 이벤트 (현재는 사용하지 않음, 필요시 주석 해제)
        # self.root.bind("<MouseWheel>", self.on_mousewheel)
        # self.main_frame.bind("<MouseWheel>", self.on_mousewheel)

    def create_menu_bar(self):
        """도움말 메뉴만 있는 메뉴 바 생성"""
        menubar = tk.Menu(self.root)
        
        # 도움말 메뉴
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="사용 설명서 (F1)", command=self.show_manual)
        help_menu.add_command(label="프로그램 정보", command=self.show_about)
        menubar.add_cascade(label="도움말", menu=help_menu)
        
        self.root.config(menu=menubar)
        
        # F1 키를 사용 설명서와 연결
        self.root.bind("<F1>", lambda event: self.show_manual())

    def show_manual(self):
        """사용 설명서 보기"""
        manual_window = tk.Toplevel(self.root)
        manual_window.title("Vision Brightness Calibration 사용 설명서")
        manual_window.geometry("800x600")
        manual_window.minsize(600, 400)
        
        # 프레임 생성
        frame = ttk.Frame(manual_window, padding=10)
        frame.pack(fill=tk.BOTH, expand=True)
        
        # 스크롤 가능한 텍스트 위젯
        manual_text = tk.Text(frame, wrap=tk.WORD, width=80, height=25)
        scrollbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=manual_text.yview)
        manual_text.configure(yscrollcommand=scrollbar.set)
        
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        manual_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        
        # 설명서 내용
        manual_content = """
# Vision Brightness Calibration 사용 설명서

## 프로그램 개요
이 프로그램은 이미지의 명도(밝기)를 측정하고, 카메라 DB 설정값을 최적화하기 위한 도구입니다. 전체 이미지 또는 선택 영역의 명도를 분석하여 LightStrengthGain과 ContrastOffset 값의 최적 조정을 제안합니다.

## 주요 기능

### 1. 이미지 불러오기 및 분석
- '이미지 불러오기' 버튼을 클릭하여 분석할 이미지를 선택합니다.
- '전체 이미지 분석' 버튼을 클릭하면 전체 이미지의 명도를 분석합니다.
- 이미지 위에서 마우스 드래그로 영역을 선택하면 해당 영역의 명도를 분석합니다.
- '선택 영역 초기화' 버튼으로 선택 영역을 지울 수 있습니다.

### 2. 명도 분석 결과
- 측정 결과: 선택 영역의 평균 명도, 표준편차, 최소/최대 명도, RGB 평균값
- 전체 이미지 정보: 이미지 크기, 전체 평균 명도, 표준편차, RGB 평균값
- 히스토그램: 명도 분포를 시각적으로 확인할 수 있는 그래프

### 3. DB 설정 최적화
- DB 설정: LightStrengthGain과 ContrastOffset 값을 조정할 수 있습니다.
- 권장 조정값: 현재 명도를 기반으로 목표 명도(128)에 도달하기 위한 최적의 DB 설정값을 제안합니다.
- DB 즉시 적용: 변경된 설정값을 카메라 DB에 바로 적용할 수 있습니다.

### 4. 측정 기록 관리
- 측정 결과 저장: 현재 분석 결과를 내부 기록에 저장합니다.
- 기록 보기: 저장된 측정 기록을 확인하고 이전 DB 설정값을 적용할 수 있습니다.
- Excel로 내보내기: 모든 측정 기록을 Excel 파일로 내보낼 수 있습니다.
- 보고서 생성: HTML 형식의 상세 보고서를 생성합니다.

## 단축키
- F1: 사용 설명서 열기

## 기술 문의
문제나 개선 사항이 있으면 개발자에게 문의하세요:
levi.beak@parksystems.com
"""
        
        manual_text.insert(tk.END, manual_content)
        manual_text.config(state=tk.DISABLED)  # 읽기 전용으로 설정
        
        # 닫기 버튼
        close_button = ttk.Button(manual_window, text="닫기", command=manual_window.destroy)
        close_button.pack(pady=10)

    def show_about(self):
        """프로그램 정보 보기"""
        about_window = tk.Toplevel(self.root)
        about_window.title("프로그램 정보")
        about_window.geometry("500x400")
        about_window.resizable(False, False)
        
        # 내용 프레임
        content_frame = ttk.Frame(about_window, padding=20)
        content_frame.pack(fill=tk.BOTH, expand=True)
        
        # 제목과 버전 정보
        title_label = ttk.Label(content_frame, text="Vision Brightness Calibration", font=("Arial", 16, "bold"))
        title_label.pack(pady=10)
        
        # 제품 정보 프레임
        prod_frame = ttk.LabelFrame(content_frame, text="제품 정보")
        prod_frame.pack(fill=tk.X, pady=10)
        
        version_frame = ttk.Frame(prod_frame)
        version_frame.pack(fill=tk.X, pady=2)
        ttk.Label(version_frame, text="버전:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        ttk.Label(version_frame, text="1.0.0").pack(side=tk.LEFT, padx=5)
        
        date_frame = ttk.Frame(prod_frame)
        date_frame.pack(fill=tk.X, pady=2)
        ttk.Label(date_frame, text="출시일:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        ttk.Label(date_frame, text="2025-02-04").pack(side=tk.LEFT, padx=5)
        
        # 개발 정보 프레임
        dev_frame = ttk.LabelFrame(content_frame, text="개발 정보")
        dev_frame.pack(fill=tk.X, pady=10)
        
        dev_frame1 = ttk.Frame(dev_frame)
        dev_frame1.pack(fill=tk.X, pady=2)
        ttk.Label(dev_frame1, text="개발자:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        ttk.Label(dev_frame1, text="Levi Beak / 박광림").pack(side=tk.LEFT, padx=5)
        
        dev_frame2 = ttk.Frame(dev_frame)
        dev_frame2.pack(fill=tk.X, pady=2)
        ttk.Label(dev_frame2, text="소속:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        ttk.Label(dev_frame2, text="Quality Assurance Team").pack(side=tk.LEFT, padx=5)
        
        dev_frame3 = ttk.Frame(dev_frame)
        dev_frame3.pack(fill=tk.X, pady=2)
        ttk.Label(dev_frame3, text="이메일:", width=15, anchor=tk.W).pack(side=tk.LEFT, padx=5)
        ttk.Label(dev_frame3, text="levi.beak@parksystems.com").pack(side=tk.LEFT, padx=5)
        
        # 프로그램 설명 프레임
        desc_frame = ttk.LabelFrame(content_frame, text="프로그램 설명")
        desc_frame.pack(fill=tk.X, pady=10)
        
        desc_text = tk.Text(desc_frame, wrap=tk.WORD, height=6, width=50)
        desc_text.pack(pady=5, padx=5, fill=tk.X)
        desc_text.insert(tk.END, "Vision Brightness Calibration은 이미지의 명도를 측정하고 카메라 DB 설정을 최적화하기 위한 도구입니다.\n\n주요 기능:\n• 이미지 명도 분석\n• 카메라 DB 값 최적화 제안\n• 측정 기록 관리 및 보고서 생성")
        desc_text.config(state=tk.DISABLED)

        # 닫기 버튼 추가
        close_button = ttk.Button(about_window, text="닫기", command=about_window.destroy)
        close_button.pack(pady=10)
        
    def validate_float_input(self, value):
        """입력값이 0~1 사이의 유효한 소수점 값인지 검증"""
        if value == "":
            return True
        try:
            val = float(value)
            if val < 0 or val > 1:
                return False
            return True
        except ValueError:
            return False
        
    def update_light_strength(self, *args):
        """LightStrengthGain 슬라이더 변경 시 Entry 업데이트"""
        try:
            value = self.light_strength_var.get()
            # 값이 변경되었을 때만 Entry 업데이트
            current_text = self.light_strength_entry.get()
            formatted_value = f"{value:.2f}"
            if current_text != formatted_value:
                self.light_strength_entry.delete(0, tk.END)
                self.light_strength_entry.insert(0, formatted_value)
        except:
            pass
            
    def zoom_in(self):
        """이미지 확대"""
        if self.image is None:
            return
        self.zoom_factor *= 1.2
        self.display_image()
        
    def zoom_out(self):
        """이미지 축소"""
        if self.image is None:
            return
        self.zoom_factor /= 1.2
        if self.zoom_factor < 0.1:  # 최소 줌 제한
            self.zoom_factor = 0.1
        self.display_image()
        
    def zoom_reset(self):
        """원본 크기로 복원"""
        if self.image is None:
            return
        self.zoom_factor = 1.0
        self.display_image()
        
    def init_histogram(self):
        """초기 빈 히스토그램 표시"""
        self.ax.clear()
        self.ax.set_title("명도 분포 히스토그램", fontsize=12)
        self.ax.set_xlabel("명도 값 (0-255)", fontsize=10)
        self.ax.set_ylabel("픽셀 수", fontsize=10)
        self.ax.text(0.5, 0.5, '이미지를 불러오면 히스토그램이 표시됩니다', 
                    horizontalalignment='center', verticalalignment='center', 
                    transform=self.ax.transAxes)
        self.canvas_hist.draw()
        
    def recalculate_recommendations(self):
        """DB 설정값 변경 후 권장 조정값 재계산"""
        if self.current_avg_brightness > 0:  # 명도 측정이 된 경우에만 실행
            self.calculate_recommendations(self.current_avg_brightness)
        else:
            messagebox.showinfo("알림", "먼저 이미지를 분석해주세요.")

    def calculate_recommendations(self, avg_brightness):
        """명도에 기반한 DB 설정값을 계산하고 UI에 표시합니다."""
        recommendations = self._generate_recommendation_text(
            avg_brightness,
            self.TARGET_BRIGHTNESS,
            self.light_strength_var.get(),
            self.is_full_image_analysis
        )
        
        # Text 위젯 업데이트
        self._update_recommendation_widget(recommendations)

    @staticmethod
    def _generate_recommendation_text(avg_brightness, target_brightness, current_light_strength, is_full_analysis):
        """밝기 값에 따라 권장 조정값 텍스트 목록을 생성합니다."""
        recommendations = []
        
        # 분석 유형에 따른 문구 추가
        analysis_type = "전체 이미지" if is_full_analysis else "선택 영역"
        header_text = f"[{analysis_type} 분석 결과]"
        recommendations.append(header_text)
        
        if abs(avg_brightness - target_brightness) <= 10:
            recommendations.append(f"현재 명도({avg_brightness:.2f})가 목표값(128±10)에 근접합니다. 조정이 불필요합니다.")
        else:
            # 로직 상세 설명 추가
            if avg_brightness > target_brightness:
                # 너무 밝음 - LightStrengthGain 감소 필요
                brightness_diff = avg_brightness - target_brightness
                
                # 현재 LightStrengthGain 값에 비례하여 조정량 계산
                adjustment_factor = current_light_strength  # 현재 DB 값을 조정 계수로 사용
                adjustment = (brightness_diff / 255) * adjustment_factor
                
                new_light_strength = max(0.0, current_light_strength - adjustment)
                
                recommendations.append(f"명도({avg_brightness:.2f})가 목표(128)보다 {brightness_diff:.1f} 높습니다.")
                recommendations.append(f"LightStrengthGain을 {current_light_strength:.2f}에서 {new_light_strength:.2f}로 감소시키는 것을 권장합니다.")
                recommendations.append(f"조정량: -{adjustment:.3f} (= -{brightness_diff:.1f}/255 * {adjustment_factor:.2f})")
            else:
                # 너무 어두움 - LightStrengthGain 증가 필요
                brightness_diff = target_brightness - avg_brightness
                
                # 조정 가능한 여유 범위 (1.0 - 현재값)
                adjustment_factor = 1.0 - current_light_strength
                if adjustment_factor < 0.1:
                    adjustment_factor = 0.1
                
                adjustment = (brightness_diff / 255) * adjustment_factor
                
                new_light_strength = min(1.0, current_light_strength + adjustment)
                
                recommendations.append(f"명도({avg_brightness:.2f})가 목표(128)보다 {brightness_diff:.1f} 낮습니다.")
                recommendations.append(f"LightStrengthGain을 {current_light_strength:.2f}에서 {new_light_strength:.2f}로 증가시키는 것을 권장합니다.")
                recommendations.append(f"조정량: +{adjustment:.3f} (= +{brightness_diff:.1f}/255 * {adjustment_factor:.2f})")
        
        return recommendations

    def _update_recommendation_widget(self, recommendations):
        """권장 조정값 Text 위젯의 내용을 업데이트합니다."""
        if not recommendations:
            return
            
        # Text 위젯 업데이트
        self.recommend_text.config(state=tk.NORMAL)  # 편집 가능하게 변경
        self.recommend_text.delete(1.0, tk.END)  # 내용 지우기
        
        # 첫 줄에 헤더 스타일 적용
        self.recommend_text.insert(tk.END, recommendations[0]+"\n", "header")
        
        # 나머지 텍스트는 일반 스타일로 추가하되, 권장 값 부분은 강조
        if len(recommendations) > 1:
            self.recommend_text.insert(tk.END, recommendations[1]+"\n", "normal")
            
            if len(recommendations) > 2:
                # 권장 값 라인은 특별히 처리 (두 번째 라인)
                second_line = recommendations[2]
                
                # "에서" 와 "로" 사이의 값을 강조
                if "에서" in second_line and "로" in second_line:
                    parts = second_line.split("에서")
                    start_part = parts[0] + "에서"
                    
                    remaining = parts[1].split("로")
                    value_part = remaining[0]  # 강조할 값
                    end_part = "로" + remaining[1]
                    
                    # 색상 강조 태그 설정 (없으면 추가)
                    if not "value" in self.recommend_text.tag_names():
                        self.recommend_text.tag_configure("value", font=("Arial", 11, "bold"), foreground="red")
                    
                    # 화살표 태그 추가
                    if not "arrow" in self.recommend_text.tag_names():
                        self.recommend_text.tag_configure("arrow", font=("Arial", 11), foreground="blue")
                    
                    # 텍스트 추가 (권장 값 강조)
                    self.recommend_text.insert(tk.END, start_part, "normal")
                    self.recommend_text.insert(tk.END, value_part, "value")
                    
                    # 화살표 기호 추가하여 변경을 시각적으로 표시
                    arrow = " → " if "증가" in end_part else " ↓ "
                    self.recommend_text.insert(tk.END, arrow, "arrow")
                    
                    self.recommend_text.insert(tk.END, end_part+"\n", "normal")
                else:
                    # 기본 형식이 아닌 경우 일반 텍스트로 추가
                    self.recommend_text.insert(tk.END, second_line+"\n", "normal")
                
                # 나머지 라인 추가
                for line in recommendations[3:]:
                    self.recommend_text.insert(tk.END, line+"\n", "normal")
        
        self.recommend_text.config(state=tk.DISABLED)  # 다시 읽기 전용으로 설정

    def load_image(self):
        """이미지 파일 불러오기"""
        file_path = filedialog.askopenfilename(
            title="이미지 선택",
            filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")]
        )
        
        if not file_path:
            return
        
        try:
            # PIL로 이미지 로드
            self.pil_image = Image.open(file_path)
            
            # RGB 이미지로 변환 (RGBA 등 다른 모드일 경우 대비)
            if self.pil_image.mode != 'RGB':
                self.pil_image = self.pil_image.convert('RGB')
                
            # PIL 이미지를 NumPy 배열로 변환 후 BGR로 변환 (OpenCV 형식)
            self.image = cv2.cvtColor(np.array(self.pil_image), cv2.COLOR_RGB2BGR)
            
            if self.image is None:
                messagebox.showerror("오류", "이미지를 불러올 수 없습니다.")
                return
            
            # 줌 팩터 초기화
            self.zoom_factor = 1.0
            
            # DB 값 불러오기
            self.load_db_values()
            
            self.display_image()
            self.reset_selection()
            self.analyze_full_image()  # 전체 이미지 분석
            
        except Exception as e:
            messagebox.showerror("오류", f"이미지 불러오기 오류: {str(e)}")
            print(f"상세 오류: {e}")  # 디버깅용
    
    def display_image(self):
        """이미지를 캔버스에 표시"""
        if self.image is None:
            return
            
        # 원본 이미지 크기
        h, w = self.image.shape[:2]
        self.image_size_label.config(text=f"{w} x {h} 픽셀")
        
        # 이미지 크기 계산 (줌 팩터 적용)
        display_w = int(w * self.scale_factor * self.zoom_factor)
        display_h = int(h * self.scale_factor * self.zoom_factor)
        
        # 스크롤 영역 설정을 위한 이미지 크기 계산
        container_w = self.canvas_container.winfo_width()
        container_h = self.canvas_container.winfo_height()
        
        # 처음 불러올 때는 컨테이너 크기가 0일 수 있음
        if container_w <= 1:
            container_w = self.max_image_width
        if container_h <= 1:
            container_h = self.max_image_height
        
        # 이미지가 컨테이너보다 작으면 그대로 표시, 크면 스케일링 적용
        if w <= container_w and h <= container_h and self.zoom_factor <= 1.0:
            self.scale_factor = 1.0  # 원본 크기 유지
        else:
            # 이미지 크기가 큰 경우 적절하게 축소
            self.scale_factor = min(container_w/w, container_h/h)
            
        # 최종 표시 크기 계산 (줌 팩터 적용)
        display_w = int(w * self.scale_factor * self.zoom_factor)
        display_h = int(h * self.scale_factor * self.zoom_factor)
        
        # 이미지 리사이징
        resized = cv2.resize(self.image, (display_w, display_h))
        resized = cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
        
        self.tk_image = ImageTk.PhotoImage(image=Image.fromarray(resized))
        
        # 캔버스 크기 및 스크롤 영역 설정
        self.canvas.config(scrollregion=(0, 0, display_w, display_h), width=container_w, height=container_h)
        
        # 이전 이미지 삭제
        self.canvas.delete("all")
        
        # 새 이미지 표시
        self.canvas.create_image(0, 0, image=self.tk_image, anchor=tk.NW, tags="image")
    
    def analyze_full_image(self):
        """전체 이미지의 명도 분석"""
        if self.image is None:
            messagebox.showinfo("알림", "먼저 이미지를 불러와주세요.")
            return
        
        stats = self._calculate_image_stats(self.image)
        if not stats:
            return
        
        # 현재 명도 저장
        self.current_avg_brightness = stats['avg_brightness']
        self.is_full_image_analysis = True
        
        # 결과 표시
        self.full_brightness_label.config(text=f"{stats['avg_brightness']:.2f} / 255")
        self.full_std_label.config(text=f"{stats['std_brightness']:.2f}")
        
        # 전체 이미지 정보 프레임에 RGB 평균 추가
        rgb_info = f"R:{stats['avg_r']:.0f}, G:{stats['avg_g']:.0f}, B:{stats['avg_b']:.0f}"
        
        # RGB 정보를 표시할 레이블이 없으면 새로 만듭니다
        if not hasattr(self, 'full_rgb_label'):
            ttk.Label(self.full_image_frame, text="평균 RGB:").grid(row=3, column=0, sticky=tk.W, padx=5, pady=2)
            self.full_rgb_label = ttk.Label(self.full_image_frame, text="-")
            self.full_rgb_label.grid(row=3, column=1, sticky=tk.W, padx=5, pady=2)
        self.full_rgb_label.config(text=rgb_info)
        
        # 선택 영역 결과 초기화
        self.region_label.config(text="-")
        self.brightness_label.config(text="-")
        self.std_label.config(text="-")
        self.min_max_label.config(text="-")
        if hasattr(self, 'rgb_label'):
            self.rgb_label.config(text="-")
        
        # 히스토그램 업데이트
        self.update_histogram(stats['luminance_channel'], is_full=True)
        
        # 권장 조정값 계산 (전체 이미지 기준)
        self.calculate_recommendations(stats['avg_brightness'])
    
    def reset_selection(self):
        """선택 영역 초기화"""
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
            self.selection_rect = None
        
        # 콤보박스를 "직접 선택"으로 되돌림
        self.preset_combo.current(0)
        
        self.region_label.config(text="-")
        self.brightness_label.config(text="-")
        self.std_label.config(text="-")
        self.min_max_label.config(text="-")
        self.current_avg_brightness = 0
        self.is_full_image_analysis = False
        
        # Text 위젯의 내용 지우기
        self.recommend_text.config(state=tk.NORMAL)
        self.recommend_text.delete(1.0, tk.END)
        self.recommend_text.config(state=tk.DISABLED)
    
    def on_preset_selected(self, event):
        """선택 영역 프리셋 선택 시 호출되는 함수"""
        if self.image is None:
            messagebox.showinfo("알림", "먼저 이미지를 불러와주세요.")
            self.preset_combo.current(0)  # "직접 선택"으로 되돌림
            return
            
        selected = self.preset_combo.get()
        
        if selected == "직접 선택":
            # 선택 영역만 초기화 (이미지는 유지)
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
                self.selection_rect = None
            return
            
        elif selected == "기준 영역 (70,100)-(400,300)":
            # 이전 선택 영역 삭제
            if self.selection_rect:
                self.canvas.delete(self.selection_rect)
            
            # 기본 선택 영역 좌표 설정
            self.start_x = 70 * self.scale_factor * self.zoom_factor
            self.start_y = 100 * self.scale_factor * self.zoom_factor
            self.end_x = 400 * self.scale_factor * self.zoom_factor
            self.end_y = 300 * self.scale_factor * self.zoom_factor
            
            # 새 선택 영역 생성
            self.selection_rect = self.canvas.create_rectangle(
                self.start_x, self.start_y, self.end_x, self.end_y,
                outline="red", width=2
            )
            
            # 선택 영역의 명도 계산
            self.calculate_brightness()
    
    def on_mouse_down(self, event):
        """마우스 버튼을 누를 때 호출"""
        if self.image is None:
            return
            
        self.start_x = self.canvas.canvasx(event.x)  # 스크롤 위치 고려
        self.start_y = self.canvas.canvasy(event.y)  # 스크롤 위치 고려
        self.is_selecting = True
        self.is_full_image_analysis = False
        
        # 이전 선택 영역 삭제
        if self.selection_rect:
            self.canvas.delete(self.selection_rect)
        
        # 새 선택 영역 생성
        self.selection_rect = self.canvas.create_rectangle(
            self.start_x, self.start_y, self.start_x, self.start_y,
            outline="red", width=2
        )
    
    def on_mouse_move(self, event):
        """마우스를 드래그할 때 호출"""
        if not self.is_selecting:
            return
            
        self.end_x = self.canvas.canvasx(event.x)  # 스크롤 위치 고려
        self.end_y = self.canvas.canvasy(event.y)  # 스크롤 위치 고려
        
        # 선택 영역 업데이트
        self.canvas.coords(self.selection_rect, self.start_x, self.start_y, self.end_x, self.end_y)
    
    def on_mouse_up(self, event):
        """마우스 버튼을 놓을 때 호출"""
        if not self.is_selecting or self.image is None:
            return
            
        self.end_x = self.canvas.canvasx(event.x)  # 스크롤 위치 고려
        self.end_y = self.canvas.canvasy(event.y)  # 스크롤 위치 고려
        self.is_selecting = False
        
        # 선택 영역의 명도 계산
        self.calculate_brightness()
    
    def calculate_brightness(self):
        """선택 영역의 평균 명도 계산"""
        if self.image is None:
            return
            
        # 캔버스 좌표를 실제 이미지 좌표로 변환 (줌 팩터 고려)
        scale = self.scale_factor * self.zoom_factor
        x1 = int(min(self.start_x, self.end_x) / scale)
        y1 = int(min(self.start_y, self.end_y) / scale)
        x2 = int(max(self.start_x, self.end_x) / scale)
        y2 = int(max(self.start_y, self.end_y) / scale)
        
        # 이미지 크기 범위 내로 조정
        h, w = self.image.shape[:2]
        x1, y1 = max(0, x1), max(0, y1)
        x2, y2 = min(w, x2), min(h, y2)
        
        if x2 <= x1 or y2 <= y1:
            self.region_label.config(text="유효하지 않은 영역")
            return
        
        # 선택 영역 표시
        self.region_label.config(text=f"({x1}, {y1}) - ({x2}, {y2})")
        
        # 선택 영역 추출
        roi = self.image[y1:y2, x1:x2]
        
        stats = self._calculate_image_stats(roi)
        if not stats:
            return
        
        # 현재 명도 저장
        self.current_avg_brightness = stats['avg_brightness']
        
        # 결과 표시
        self.brightness_label.config(text=f"{stats['avg_brightness']:.2f} / 255")
        self.std_label.config(text=f"{stats['std_brightness']:.2f}")
        self.min_max_label.config(text=f"{stats['min_brightness']:.0f} / {stats['max_brightness']:.0f}")
        
        # 결과 프레임에 RGB 평균 추가 (기존 인터페이스에 추가)
        rgb_info = f"R:{stats['avg_r']:.0f}, G:{stats['avg_g']:.0f}, B:{stats['avg_b']:.0f}"
        
        # RGB 정보를 표시할 레이블이 없으면 새로 만듭니다
        if not hasattr(self, 'rgb_label'):
            ttk.Label(self.result_frame, text="평균 RGB:").grid(row=4, column=0, sticky=tk.W, padx=5, pady=2)
            self.rgb_label = ttk.Label(self.result_frame, text="-")
            self.rgb_label.grid(row=4, column=1, sticky=tk.W, padx=5, pady=2)
        self.rgb_label.config(text=rgb_info)
        
        # 권장 조정값 계산
        self.calculate_recommendations(stats['avg_brightness'])
        
        # 히스토그램 업데이트
        self.update_histogram(stats['luminance_channel'])

    def _calculate_image_stats(self, image_roi):
        """주어진 이미지 영역(ROI)의 명도 및 색상 통계를 계산합니다."""
        if image_roi is None or image_roi.size == 0:
            return None

        # BGR을 RGB로 변환
        rgb_roi = cv2.cvtColor(image_roi, cv2.COLOR_BGR2RGB)

        # 채널 분리 및 Luminance 계산 (Y' = 0.299*R' + 0.587*G' + 0.114*B')
        r = rgb_roi[:, :, 0].astype(float)
        g = rgb_roi[:, :, 1].astype(float)
        b = rgb_roi[:, :, 2].astype(float)
        luminance = 0.299 * r + 0.587 * g + 0.114 * b

        return {
            'luminance_channel': luminance.astype(np.uint8),
            'avg_brightness': np.mean(luminance),
            'std_brightness': np.std(luminance),
            'min_brightness': np.min(luminance),
            'max_brightness': np.max(luminance),
            'avg_r': np.mean(r),
            'avg_g': np.mean(g),
            'avg_b': np.mean(b),
        }

    def update_histogram(self, v_channel, is_full=False):
        """명도 분포 히스토그램 업데이트"""
        self.ax.clear()
        
        # 히스토그램 데이터 생성
        hist, bins = np.histogram(v_channel.flatten(), 256, [0, 256])
        
        # 히스토그램 그리기
        self.ax.bar(bins[:-1], hist, width=1, color='gray', alpha=0.7)
        
        # 평균선과 목표선 표시
        mean_val = np.mean(v_channel)
        self.ax.axvline(x=self.TARGET_BRIGHTNESS, color='r', linestyle='--', label=f'목표({self.TARGET_BRIGHTNESS})')
        self.ax.axvline(x=mean_val, color='b', linestyle='-', label=f'평균({mean_val:.1f})')
        
        # 제목과 레이블 설정
        title = "전체 이미지 명도 분포 (Luminance)" if is_full else "선택 영역 명도 분포 (Luminance)"
        self.ax.set_title(title, fontsize=12)
        self.ax.set_xlabel("명도 값 (0-255)", fontsize=10)
        self.ax.set_ylabel("픽셀 수", fontsize=10)
        
        # 범례 위치 조정
        self.ax.legend(loc='upper right', fontsize='small')
        
        # 축 레이블이 잘 보이도록 여백 조정
        self.fig.tight_layout()
        self.canvas_hist.draw()

    def save_measurement(self, comment=""):
        """현재 측정 결과를 기록에 추가"""
        if self.current_avg_brightness <= 0:
            messagebox.showinfo("알림", "저장할 측정 결과가 없습니다.")
            return
        
        # 현재 측정 정보 수집
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        image_name = "전체 이미지" if self.is_full_image_analysis else "선택 영역"
        
        if self.is_full_image_analysis:
            region = "전체"
            brightness = self.full_brightness_label.cget("text").split('/')[0].strip()
            rgb = self.full_rgb_label.cget("text")
        else:
            region = self.region_label.cget("text")
            brightness = self.brightness_label.cget("text").split('/')[0].strip()
            rgb = self.rgb_label.cget("text")
        
        light_strength = self.light_strength_var.get()
        recommendation = self.recommend_text.get(1.0, tk.END).strip()
        
        # 측정 항목 생성
        measurement = {
            "날짜시간": now,
            "이미지명": image_name,
            "영역": region,
            "평균명도": brightness,
            "RGB평균": rgb,
            self.KEY_LSG: f"{light_strength:.2f}",
            "권장조정값": recommendation
        }
        
        # 리스트에 추가
        self.measurements.append(measurement)
        
        # 리스트박스에 표시
        display_text = f"{now} - 명도: {brightness}, LSG: {light_strength:.2f}"
        self.history_listbox.insert(tk.END, display_text)
        
        messagebox.showinfo("저장 완료", "측정 결과가 기록에 저장되었습니다.")

    def on_history_select(self, event):
        """기록에서 항목 선택 시 해당 항목의 상세 정보 표시"""
        if not self.history_listbox.curselection():
            return
        
        index = self.history_listbox.curselection()[0]
        if index < 0 or index >= len(self.measurements):
            return
        
        # 선택한 기록 정보
        selected = self.measurements[index]
        
        # 팝업 창으로 상세 정보 표시
        detail_window = tk.Toplevel(self.root)
        detail_window.title("측정 기록 상세 정보")
        detail_window.geometry("500x300")
        
        # 상세 정보 표시
        detail_frame = ttk.Frame(detail_window, padding=10)
        detail_frame.pack(fill=tk.BOTH, expand=True)
        
        row = 0
        for key, value in selected.items():
            ttk.Label(detail_frame, text=f"{key}:", anchor=tk.W).grid(row=row, column=0, sticky=tk.W, padx=5, pady=2)
            ttk.Label(detail_frame, text=value, wraplength=350).grid(row=row, column=1, sticky=tk.W, padx=5, pady=2)
            row += 1
        
        # DB 값 적용 버튼
        apply_btn = ttk.Button(detail_frame, text="이 DB 값 적용", 
                               command=lambda: self.apply_history_db(selected))
        apply_btn.grid(row=row, column=0, columnspan=2, pady=10)

    def apply_history_db(self, history_item):
        """기록에서 선택한 DB 값을 현재 설정에 적용"""
        try:
            light_strength = float(history_item[self.KEY_LSG])
            self.light_strength_var.set(light_strength)
            
            # 재계산
            self.recalculate_recommendations()
            
            messagebox.showinfo("적용 완료", "선택한 기록의 DB 값이 적용되었습니다.")
        except Exception as e:
            messagebox.showerror("오류", f"DB 값 적용 중 오류 발생: {str(e)}")

    def export_to_excel(self):
        """측정 기록을 Excel 파일로 내보내기"""
        if not self.measurements:
            messagebox.showinfo("알림", "내보낼 측정 기록이 없습니다.")
            return
        
        try:
            # 파일 저장 대화상자
            file_path = filedialog.asksaveasfilename(
                defaultextension=".xlsx",
                filetypes=[("Excel 파일", "*.xlsx"), ("모든 파일", "*.*")],
                title="Excel 파일 저장"
            )
            
            if not file_path:
                return
            
            # DataFrame 생성
            df = pd.DataFrame(self.measurements)
            
            # Excel 파일로 저장
            df.to_excel(file_path, index=False)
            
            messagebox.showinfo("내보내기 완료", f"측정 기록이 {file_path}에 저장되었습니다.")
        
        except Exception as e:
            messagebox.showerror("오류", f"Excel 내보내기 중 오류 발생: {str(e)}")

    def _get_camera_xml_path(self):
        """General.xml을 파싱하여 Camera XML 파일 경로와 이름을 반환합니다."""
        base_path = r"C:\Park Systems\XEService\DB\Module\Vision"
        general_xml_path = os.path.join(base_path, "Module", "General.xml")

        if not os.path.exists(general_xml_path):
            messagebox.showerror("오류", f"General.xml 파일을 찾을 수 없습니다: {general_xml_path}")
            return None, None

        try:
            tree = ET.parse(general_xml_path)
            root = tree.getroot()

            camera_name = None
            for part in root.findall(self.XML_TAG_PART):
                if part.find(self.XML_TAG_TYPE) is not None and part.find(self.XML_TAG_TYPE).text == self.XML_TYPE_CAMERA:
                    if (name_elem := part.find(self.XML_TAG_NAME)) is not None:
                        camera_name = name_elem.text
                        break
            
            if not camera_name:
                messagebox.showinfo("알림", f"General.xml에서 {self.XML_TYPE_CAMERA} 타입의 Part를 찾을 수 없습니다.")
                return None, None

            camera_xml_path = os.path.join(base_path, "Part", "Camera", f"{camera_name}.xml")
            if not os.path.exists(camera_xml_path):
                messagebox.showinfo("알림", f"Camera XML 파일을 찾을 수 없습니다: {camera_xml_path}")
                return None, None

            return camera_xml_path, camera_name
        except ET.ParseError as e:
            messagebox.showerror("오류", f"XML 파일 파싱 오류: {general_xml_path}\n{e}")
            return None, None

    def apply_db_to_file(self):
        """권장 조정값을 DB 파일에 즉시 적용"""
        camera_xml_path, camera_name = self._get_camera_xml_path()
        if not camera_xml_path:
            return

        try:
            light_strength = self.light_strength_var.get()
            
            # Camera XML 파일 파싱
            camera_tree = ET.parse(camera_xml_path)
            camera_root = camera_tree.getroot()
            
            # LightStrengthGain 및 ContrastOffset 값 업데이트
            lsg_updated = False
            
            for item in camera_root.findall(self.XML_TAG_ITEM):
                name_elem = item.find(self.XML_TAG_NAME)
                if name_elem is not None:
                    if name_elem.text == self.KEY_LSG:
                        value_elem = item.find(self.XML_TAG_VALUE)
                        if value_elem is not None:
                            value_elem.text = f"{light_strength:.2f}"
                            lsg_updated = True
            
            # 업데이트된 파일 저장
            camera_tree.write(camera_xml_path, encoding="utf-8", xml_declaration=True)
            
            # 결과 메시지
            messagebox.showinfo("DB 적용 완료", 
                               f"DB 값이 {camera_xml_path}에 성공적으로 적용되었습니다.\n\n"
                               f"Camera 타입: {camera_name}\n"
                               f"LightStrengthGain: {light_strength:.2f}")
            
            # 측정 기록에 DB 적용 내역 추가
            self.save_measurement(f"DB 파일에 적용: {camera_name}.xml")
        
        except Exception as e:
            messagebox.showerror("오류", f"DB 파일 업데이트 중 오류 발생: {str(e)}")
            print(f"상세 오류: {e}")  # 디버깅용

    def generate_report(self):
        """분석 보고서 생성"""
        if not self.measurements:
            messagebox.showinfo("알림", "보고서에 포함할 측정 기록이 없습니다.")
            return
        
        try:
            # 파일 저장 대화상자
            file_path = filedialog.asksaveasfilename(
                defaultextension=".html",
                filetypes=[("HTML 파일", "*.html"), ("모든 파일", "*.*")],
                title="분석 보고서 저장"
            )
            
            if not file_path:
                return
            
            # 템플릿 파일 읽기
            try:
                template_path = os.path.join(os.path.dirname(__file__), "report_template.html")
                with open(template_path, 'r', encoding='utf-8') as t:
                    template = t.read()
            except FileNotFoundError:
                messagebox.showerror("오류", "report_template.html 파일을 찾을 수 없습니다.")
                return

            # 테이블 헤더 생성
            table_header_html = "".join(f'<th>{col}</th>' for col in self.measurement_columns)

            # 테이블 데이터 행 생성
            table_rows_html = ""
            for measurement in self.measurements:
                table_rows_html += '<tr>'
                for col in self.measurement_columns:
                    table_rows_html += f'<td>{measurement.get(col, "")}</td>'
                table_rows_html += '</tr>\n'

            # 템플릿에 데이터 채우기
            report_content = template.replace('{{total_measurements}}', str(len(self.measurements)))
            report_content = report_content.replace('{{report_time}}', datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
            report_content = report_content.replace('{{table_header}}', table_header_html)
            report_content = report_content.replace('{{table_rows}}', table_rows_html)

            # 완성된 HTML을 파일에 쓰기
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(report_content)
            
            # 성공 메시지
            messagebox.showinfo("보고서 생성 완료", f"분석 보고서가 {file_path}에 저장되었습니다.")
            
            # 브라우저에서 열기
            webbrowser.open(file_path)
        except Exception as e:
            messagebox.showerror("오류", f"보고서 생성 중 오류 발생: {str(e)}")

    def on_frame_configure(self, event):
        """스크롤 프레임 크기가 변경되면 스크롤 영역 업데이트"""
        self.main_canvas.configure(scrollregion=self.main_canvas.bbox("all"))

    def on_canvas_configure(self, event):
        """캔버스 크기가 변경되면 내부 프레임 너비 조정"""
        canvas_width = event.width
        self.main_canvas.itemconfig(self.canvas_frame_id, width=canvas_width)

    def on_mousewheel(self, event):
        """마우스 휠 이벤트 처리"""
        self.main_canvas.yview_scroll(int(-1*(event.delta/120)), "units")

    def load_db_values(self):
        """DB 파일에서 설정값 불러오기"""
        camera_xml_path, camera_name = self._get_camera_xml_path()
        if not camera_xml_path:
            return

        try:
            # Camera XML 파일 파싱
            camera_tree = ET.parse(camera_xml_path)
            camera_root = camera_tree.getroot()
            db_values = {}
            
            for item in camera_root.findall(self.XML_TAG_ITEM):
                name_elem = item.find(self.XML_TAG_NAME)
                if name_elem is not None:
                    if name_elem.text == self.KEY_LSG:
                        value_elem = item.find(self.XML_TAG_VALUE)
                        if value_elem is not None:
                            try:
                                db_values[name_elem.text] = float(value_elem.text)
                            except (ValueError, TypeError):
                                db_values[name_elem.text] = 0.0
            
            # DB 값 설정
            if self.KEY_LSG in db_values:
                self.light_strength_var.set(db_values[self.KEY_LSG])
                self.original_db_values[self.KEY_LSG] = db_values[self.KEY_LSG]
            
            # 성공 메시지
            messagebox.showinfo("DB 불러오기 완료", 
                               f"Camera({camera_name}) XML 파일에서 DB 값을 불러왔습니다.\n\n"
                               f"LightStrengthGain: {self.light_strength_var.get():.2f}")
        
        except Exception as e:
            messagebox.showerror("오류", f"DB 값 불러오기 중 오류 발생: {str(e)}")
            print(f"상세 오류: {e}")  # 디버깅용

    def reset_db_value(self, value_name):
        """특정 DB 값을 원래 값으로 초기화"""
        if value_name == self.KEY_LSG:
            self.light_strength_var.set(self.original_db_values[self.KEY_LSG])
        
        # 값이 변경되었음을 프로그램에 알림
        if self.current_avg_brightness > 0:
            self.recalculate_recommendations()

    def clear_measurement_history(self):
        """측정 기록 초기화"""
        if self.measurements:
            confirm = messagebox.askyesno("측정 기록 초기화", 
                                         "모든 측정 기록이 삭제됩니다.\n계속하시겠습니까?")
            if confirm:
                # 측정 기록 초기화
                self.measurements = []
                self.history_listbox.delete(0, tk.END)
                messagebox.showinfo("알림", "측정 기록이 초기화되었습니다.")
        else:
            messagebox.showinfo("알림", "초기화할 측정 기록이 없습니다.")

class AppController:
    """애플리케이션의 시작 순서와 생명주기를 관리하는 컨트롤러"""
    def __init__(self):
        self.root = tk.Tk()
        self.root.withdraw()  # 메인 윈도우를 시작 시 숨김

        # Tkinter 이벤트 루프가 시작된 후 체크리스트를 실행하도록 예약
        self.root.after(10, self.run_checklist)
        self.root.mainloop()

    def run_checklist(self):
        """사전 체크리스트 대화상자를 실행하고 결과를 처리합니다."""
        try:
            checklist_items = [
                "White balance 및 vimba setting 완료 상태 확인"
            ]
            checklist_dialog = ChecklistDialog(self.root, checklist_items)
            self.root.wait_window(checklist_dialog)  # 대화상자가 닫힐 때까지 대기

            if checklist_dialog.proceed:
                self.start_main_app()
            else:
                self.root.destroy()
        except Exception as e:
            messagebox.showerror("치명적 오류", f"프로그램 시작 중 오류가 발생했습니다: {e}")
            self.root.destroy()

    def start_main_app(self):
        """메인 애플리케이션 창을 초기화하고 화면에 표시합니다."""
        self.root.deiconify()  # 메인 윈도우를 다시 표시
        self.app = 명도측정프로그램(self.root)

if __name__ == "__main__":
    # AppController를 통해 애플리케이션을 시작합니다.
    AppController()
