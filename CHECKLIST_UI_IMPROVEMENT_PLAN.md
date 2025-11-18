# 체크리스트 UI 개선 계획서

## 📋 프로젝트 개요

**파일**: `src/gui/checklist_dialog.py`
**목적**: Vision Brightness Calibration 프로그램의 사전 준비사항 체크리스트 UI/UX 개선
**버전**: 1.3.0 (개선 예정)
**작성일**: 2025-11-18

---

## 🎯 선택된 개선 항목

1. ✅ 진행률 표시 추가
2. ✅ 시각적 피드백 강화
3. ✅ 색상 및 시각적 계층 구조
4. ✅ 툴팁/도움말 추가
5. ✅ 버튼 UX 개선
6. ✅ 레이아웃 개선

---

## 📐 상세 설계

### 1. 진행률 표시 추가

#### 1.1 전체 진행률 바
**위치**: 제목 바로 아래
**구성 요소**:
- `ttk.Progressbar` 위젯 사용
- 텍스트 레이블: "완료: X/Y 항목 (Z%)"
- 색상 코딩:
  - 0-50%: 빨간색 계열 (#FF4444)
  - 51-99%: 주황색 계열 (#FFA500)
  - 100%: 초록색 계열 (#4CAF50)

**구현 방법**:
```python
# 프로그레스 바 프레임
progress_frame = ttk.Frame(main_frame)
progress_label = ttk.Label(progress_frame, text="완료: 0/14 항목 (0%)")
progress_bar = ttk.Progressbar(progress_frame, length=760, mode='determinate')
```

#### 1.2 카테고리별 완료 상태
**구성 요소**:
- 각 카테고리 제목 옆에 상태 아이콘 추가
  - ✓ (완료): 모든 항목 체크 시
  - ⚠ (진행중): 일부 항목 체크 시
  - ○ (미완료): 항목 없음 시
- 카테고리별 진행률 퍼센트 표시 (예: "2/3")

**구현 방법**:
```python
category_title = f"{category} [{checked}/{total}]"
status_icon = "✓" if checked == total else "⚠" if checked > 0 else "○"
```

---

### 2. 시각적 피드백 강화

#### 2.1 체크된 항목 스타일 변경
**효과**:
- 체크된 항목: 회색 텍스트 (#888888) + 취소선
- 미체크 항목: 기본 검정 텍스트 (#000000)

**구현 방법**:
```python
# 커스텀 스타일 생성
style = ttk.Style()
style.configure('Checked.TCheckbutton', foreground='#888888')
style.configure('Unchecked.TCheckbutton', foreground='#000000')

# 동적으로 스타일 변경
def on_check_toggle(var, checkbutton):
    if var.get():
        checkbutton.configure(style='Checked.TCheckbutton')
    else:
        checkbutton.configure(style='Unchecked.TCheckbutton')
```

#### 2.2 카테고리 프레임 색상 코딩
**효과**:
- 완료: 초록색 테두리 (#4CAF50)
- 진행중: 파란색 테두리 (#2196F3)
- 미완료: 회색 테두리 (#CCCCCC)

**구현 방법**:
```python
# LabelFrame에 스타일 적용
style.configure('Completed.TLabelframe', bordercolor='#4CAF50', borderwidth=2)
style.configure('InProgress.TLabelframe', bordercolor='#2196F3', borderwidth=2)
style.configure('NotStarted.TLabelframe', bordercolor='#CCCCCC', borderwidth=1)
```

#### 2.3 카테고리 헤더 완료 아이콘
**구성 요소**:
- 카테고리 제목 앞에 상태 아이콘
- 완료 시 애니메이션 효과 (선택사항)

---

### 3. 색상 및 시각적 계층 구조

#### 3.1 색상 팔레트 정의
```python
COLORS = {
    'success': '#4CAF50',      # 초록 - 완료
    'warning': '#FFA500',      # 주황 - 진행중
    'danger': '#FF4444',       # 빨강 - 미완료/중요
    'info': '#2196F3',         # 파랑 - 정보
    'neutral': '#CCCCCC',      # 회색 - 기본
    'text_completed': '#888888', # 회색 - 완료된 텍스트
    'text_important': '#D32F2F', # 짙은 빨강 - 중요 항목
}
```

#### 3.2 중요 항목 강조
**대상 항목**:
- "White balance 설정 완료" → 빨간색 텍스트
- "Vimba Viewer 설정 완료" → 빨간색 텍스트

**구현**:
```python
important_items = ["White balance", "Vimba Viewer"]
if any(keyword in item_text for keyword in important_items):
    cb.configure(foreground=COLORS['text_important'])
```

---

### 4. 툴팁/도움말 추가

#### 4.1 항목별 도움말 데이터 구조
```python
tooltips = {
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
```

#### 4.2 툴팁 구현
**방법 1**: ToolTip 클래스 생성
```python
class ToolTip:
    def __init__(self, widget, text):
        self.widget = widget
        self.text = text
        self.tooltip_window = None
        widget.bind("<Enter>", self.show_tooltip)
        widget.bind("<Leave>", self.hide_tooltip)

    def show_tooltip(self, event=None):
        x, y, _, _ = self.widget.bbox("insert")
        x += self.widget.winfo_rootx() + 25
        y += self.widget.winfo_rooty() + 25

        self.tooltip_window = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")

        label = tk.Label(tw, text=self.text, background="#FFFFCC",
                        relief="solid", borderwidth=1, padding=5)
        label.pack()

    def hide_tooltip(self, event=None):
        if self.tooltip_window:
            self.tooltip_window.destroy()
            self.tooltip_window = None
```

#### 4.3 도움말 아이콘 추가
**구성**:
- 각 항목 옆에 "ℹ️" 또는 "?" 아이콘
- 클릭 시 상세 설명 팝업 또는 툴팁 표시

**구현**:
```python
# 각 체크박스 옆에 도움말 버튼
help_btn = ttk.Button(item_frame, text="ℹ️", width=3,
                      command=lambda txt=tooltip_text: show_help(txt))
```

---

### 5. 버튼 UX 개선

#### 5.1 프로그램 시작 버튼 강화
**변경 사항**:
- 활성화 상태: 초록색 배경 + 흰색 텍스트 + 굵은 폰트
- 비활성화 상태: 회색 배경 + "남은 항목: X개" 텍스트 표시
- 호버 효과: 약간 밝은 초록색
- 클릭 효과: 약간 어두운 초록색

**구현**:
```python
# 커스텀 스타일
style.configure('Start.TButton',
                background='#4CAF50',
                foreground='white',
                font=('Arial', 11, 'bold'),
                padding=10)

style.map('Start.TButton',
          background=[('active', '#45A049'), ('disabled', '#CCCCCC')],
          foreground=[('disabled', '#666666')])
```

#### 5.2 버튼 텍스트 동적 업데이트
```python
def update_start_button_text(self):
    remaining = self.get_remaining_items_count()
    if remaining > 0:
        self.start_button.config(text=f"프로그램 시작 (남은 항목: {remaining}개)")
    else:
        self.start_button.config(text="✓ 프로그램 시작")
```

#### 5.3 버튼 레이아웃 개선
**변경**:
- 전체 선택/해제 버튼: 좌우 배치 유지
- 프로그램 시작 버튼: 크기 확대, 녹색 강조

---

### 6. 레이아웃 개선

#### 6.1 새로운 레이아웃 구조
```
┌────────────────────────────────────────────────────────┐
│  Vision의 밝기 측정 및 Calibration 조건                 │
│  ※ White balance 및 vimba setting 완료 상태             │
├────────────────────────────────────────────────────────┤
│  완료: 11/14 항목 (79%)                                 │
│  [████████████████████████░░░░░░░░]                    │ ← 진행률 바
├────────────────────────────────────────────────────────┤
│                                                        │
│  ✓ ① 사전 완료 테스트 [2/2]                            │ ← 완료
│    ✓ White balance 설정 완료              ℹ️           │
│    ✓ Vimba Viewer 설정 완료               ℹ️           │
│                                                        │
│  ⚠ ② Camera Vision Setting [2/3]                      │ ← 진행중
│    ✓ Brightness: 50 설정 확인             ℹ️           │
│    ✓ Contrast: 0 설정 확인                ℹ️           │
│    ☐ Light Strength: 50 설정 확인         ℹ️           │
│                                                        │
│  ○ ③ Sample Focus Setting [0/2]                       │ ← 미완료
│    ☐ Tip-Sample Distance: 1.0mm 설정     ℹ️           │
│    ☐ 측정 Sample: Bare Si 준비            ℹ️           │
│                                                        │
│  ○ ④ Capture Image 저장 [0/3]                         │
│    ☐ Vision Mode: Large 선택              ℹ️           │
│    ☐ Capture: Displayed 설정              ℹ️           │
│    ☐ 이미지 측정 및 저장 완료              ℹ️           │
│                                                        │
├────────────────────────────────────────────────────────┤
│         [전체 선택]          [전체 해제]                │
│                                                        │
│         [✓ 프로그램 시작] (활성화 시 녹색)              │
└────────────────────────────────────────────────────────┘
```

#### 6.2 윈도우 크기 조정
**변경**:
- 기존: 800x620
- 신규: 850x680 (진행률 바 및 여백 추가로 높이 증가)

#### 6.3 여백 및 패딩 최적화
```python
# 메인 프레임 패딩
main_frame = ttk.Frame(self, padding=20)  # 15 → 20

# 카테고리 프레임 여백
category_frame.pack(fill=tk.X, padx=10, pady=8)  # pady 5 → 8

# 항목 패딩
cb.pack(anchor=tk.W, pady=3, padx=15)  # pady 2→3, padx 10→15
```

---

## 🔧 기술 구현 세부사항

### 1. 새로운 인스턴스 변수
```python
class ChecklistDialog(tk.Toplevel):
    def __init__(self, parent, checklist_categories):
        # 기존 변수
        self.checklist_categories = checklist_categories
        self.check_vars = {}
        self.proceed = False

        # 새로운 변수
        self.total_items = 0          # 전체 항목 수
        self.checked_items = 0        # 체크된 항목 수
        self.progress_label = None    # 진행률 레이블
        self.progress_bar = None      # 진행률 바
        self.category_frames = {}     # 카테고리 프레임 참조
        self.tooltips_data = {}       # 툴팁 데이터
```

### 2. 주요 메서드 추가

#### 2.1 진행률 업데이트
```python
def _update_progress(self):
    """전체 진행률 업데이트"""
    self.checked_items = sum(
        sum(1 for var in vars_list if var.get())
        for vars_list in self.check_vars.values()
    )
    percentage = int((self.checked_items / self.total_items) * 100)

    # 레이블 업데이트
    self.progress_label.config(
        text=f"완료: {self.checked_items}/{self.total_items} 항목 ({percentage}%)"
    )

    # 프로그레스 바 업데이트
    self.progress_bar['value'] = percentage

    # 색상 변경
    self._update_progress_color(percentage)
```

#### 2.2 카테고리 상태 업데이트
```python
def _update_category_status(self, category):
    """특정 카테고리의 상태 업데이트"""
    vars_list = self.check_vars[category]
    checked = sum(1 for var in vars_list if var.get())
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
    frame.configure(text=f"{status} {category} [{checked}/{total}]", style=style)
```

#### 2.3 툴팁 데이터 초기화
```python
def _initialize_tooltips(self):
    """툴팁 데이터 초기화"""
    self.tooltips_data = {
        "White balance 설정 완료": "Vimba Viewer에서 White Balance 자동 조정 후 설정값 확인",
        # ... (위의 tooltips 딕셔너리 내용)
    }
```

### 3. 스타일 설정
```python
def _configure_styles(self):
    """커스텀 스타일 설정"""
    style = ttk.Style()

    # LabelFrame 스타일
    style.configure('Completed.TLabelframe',
                    bordercolor='#4CAF50', borderwidth=2)
    style.configure('InProgress.TLabelframe',
                    bordercolor='#2196F3', borderwidth=2)
    style.configure('NotStarted.TLabelframe',
                    bordercolor='#CCCCCC', borderwidth=1)

    # 버튼 스타일
    style.configure('Start.TButton',
                    font=('Arial', 11, 'bold'),
                    padding=10)
    style.map('Start.TButton',
              foreground=[('!disabled', 'white'), ('disabled', '#666666')])
```

---

## 📊 위젯 계층 구조

```
ChecklistDialog (Toplevel)
└── main_frame (Frame, padding=20)
    ├── title_frame (Frame)
    │   ├── title_label (Label)
    │   └── subtitle_label (Label)
    │
    ├── progress_frame (Frame) ★ 신규
    │   ├── progress_label (Label)
    │   └── progress_bar (Progressbar)
    │
    ├── canvas (Canvas)
    │   └── scrollable_frame (Frame)
    │       └── category_frame (LabelFrame) × 4
    │           └── item_frame (Frame) × N ★ 신규
    │               ├── checkbutton (Checkbutton)
    │               └── help_button (Button) ★ 신규
    │
    └── button_frame (Frame)
        └── button_container (Frame)
            ├── select_all_btn (Button)
            ├── clear_all_btn (Button)
            └── start_button (Button, style='Start.TButton')
```

---

## 🎨 색상 적용 맵

| 요소 | 상태 | 색상 코드 | 용도 |
|------|------|-----------|------|
| 프로그레스 바 | 0-50% | #FF4444 | 미완료 경고 |
| 프로그레스 바 | 51-99% | #FFA500 | 진행중 |
| 프로그레스 바 | 100% | #4CAF50 | 완료 |
| 카테고리 테두리 | 완료 | #4CAF50 | 완료 표시 |
| 카테고리 테두리 | 진행중 | #2196F3 | 진행중 표시 |
| 카테고리 테두리 | 미완료 | #CCCCCC | 기본 |
| 체크된 항목 텍스트 | - | #888888 | 완료된 항목 |
| 중요 항목 텍스트 | - | #D32F2F | 중요 강조 |
| 시작 버튼 | 활성화 | #4CAF50 | 긍정적 액션 |
| 시작 버튼 | 비활성화 | #CCCCCC | 비활성 상태 |

---

## 📝 구현 체크리스트

### Phase 1: 기본 구조 개선
- [ ] 색상 상수 정의 (COLORS 딕셔너리)
- [ ] 스타일 설정 메서드 추가 (`_configure_styles`)
- [ ] 인스턴스 변수 추가
- [ ] 윈도우 크기 조정 (800x620 → 850x680)

### Phase 2: 진행률 표시
- [ ] 진행률 프레임 생성
- [ ] 프로그레스 바 위젯 추가
- [ ] 진행률 레이블 추가
- [ ] `_update_progress` 메서드 구현
- [ ] `_update_progress_color` 메서드 구현
- [ ] 전체 항목 수 계산 로직

### Phase 3: 카테고리 상태 표시
- [ ] 카테고리 프레임 참조 저장 (`category_frames`)
- [ ] `_update_category_status` 메서드 구현
- [ ] 카테고리 제목에 상태 아이콘 추가
- [ ] 카테고리 제목에 진행률 표시 ([X/Y])
- [ ] 카테고리별 테두리 색상 동적 변경

### Phase 4: 시각적 피드백
- [ ] 체크박스 체크 시 텍스트 색상 변경
- [ ] 중요 항목 빨간색 텍스트 적용
- [ ] 카테고리별 색상 코딩 적용

### Phase 5: 툴팁 구현
- [ ] 툴팁 데이터 딕셔너리 생성
- [ ] `ToolTip` 클래스 구현
- [ ] 각 체크박스에 툴팁 적용
- [ ] (선택사항) 도움말 버튼 추가

### Phase 6: 버튼 UX 개선
- [ ] 시작 버튼 스타일 적용
- [ ] 시작 버튼 텍스트 동적 업데이트
- [ ] 남은 항목 수 표시 로직
- [ ] 호버 효과 스타일 맵 설정

### Phase 7: 레이아웃 최적화
- [ ] 패딩 및 여백 조정
- [ ] 각 항목에 프레임 추가 (체크박스 + 도움말 버튼)
- [ ] 스크롤 영역 높이 조정

### Phase 8: 테스트 및 검증
- [ ] 각 카테고리별 체크 테스트
- [ ] 진행률 계산 정확도 확인
- [ ] 색상 전환 동작 확인
- [ ] 툴팁 표시 테스트
- [ ] 버튼 활성화/비활성화 테스트
- [ ] 전체 선택/해제 기능 테스트
- [ ] 윈도우 닫기 동작 확인

---

## 🚀 구현 우선순위

### 높음 (High Priority)
1. 진행률 표시 추가
2. 카테고리 상태 표시
3. 버튼 UX 개선

### 중간 (Medium Priority)
4. 시각적 피드백 강화
5. 색상 코딩 시스템

### 낮음 (Low Priority)
6. 툴팁 구현
7. 레이아웃 미세 조정

---

## 📌 주의사항

### 호환성
- tkinter 8.6 이상 필요 (ttk 스타일 사용)
- Windows 10/11 환경 테스트 필수
- 고해상도 디스플레이 고려

### 성능
- 체크박스 상태 변경 시 전체 UI 업데이트 최소화
- 진행률 계산은 O(n) 복잡도 유지
- 툴팁 인스턴스는 필요 시에만 생성

### 유지보수성
- 색상 코드는 중앙 집중식 관리 (COLORS 딕셔너리)
- 툴팁 텍스트는 별도 데이터 구조로 관리
- 스타일은 `_configure_styles` 메서드에서 일괄 설정

---

## 📚 참고사항

### 기존 코드와의 호환성
- `ChecklistDialog` 클래스의 public 인터페이스 유지
- `Vision_Cal.py`에서 호출하는 방식 변경 없음
- `proceed` 속성을 통한 결과 반환 방식 유지

### 테스트 파일
- `test_checklist.py` 업데이트 필요
- 새로운 기능에 대한 테스트 케이스 추가

---

## 🎯 완료 기준

### 기능적 요구사항
1. ✅ 전체 진행률이 정확하게 표시됨
2. ✅ 각 카테고리의 상태가 실시간으로 업데이트됨
3. ✅ 체크된 항목과 미체크 항목이 시각적으로 구분됨
4. ✅ 모든 항목에 도움말 툴팁이 제공됨
5. ✅ 버튼이 상태에 따라 적절하게 표시됨

### 비기능적 요구사항
1. ✅ UI 반응 속도가 기존과 동일하거나 더 빠름
2. ✅ 코드 가독성 및 유지보수성 향상
3. ✅ 기존 테스트가 모두 통과함
4. ✅ 새로운 기능에 대한 테스트 추가

---

## 📅 예상 일정

- **Phase 1-2**: 기본 구조 및 진행률 표시 (1-2시간)
- **Phase 3-4**: 카테고리 상태 및 시각적 피드백 (1-2시간)
- **Phase 5**: 툴팁 구현 (1시간)
- **Phase 6-7**: 버튼 UX 및 레이아웃 개선 (1시간)
- **Phase 8**: 테스트 및 검증 (1시간)

**총 예상 시간**: 5-7시간

---

## 🔄 버전 관리

- **현재 버전**: 1.2.0
- **목표 버전**: 1.3.0
- **변경 파일**: `src/gui/checklist_dialog.py`
- **영향받는 파일**: `Vision_Cal.py` (없음, 인터페이스 유지)

---

*이 문서는 Vision Brightness Calibration 프로젝트의 체크리스트 UI 개선을 위한 상세 계획서입니다.*
