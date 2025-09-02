# Vision Brightness Calibration v1.1.0

이미지의 명도(밝기)를 측정하고 카메라 DB 설정값을 최적화하기 위한 도구입니다.

## 주요 기능

- 이미지 명도 분석 (전체 또는 선택 영역)
- 히스토그램 시각화
- LightStrengthGain 최적값 계산
- 측정 기록 관리
- Excel 내보내기 및 HTML 보고서 생성
- Camera XML DB 파일 직접 수정

## 시스템 요구사항

- Python 3.8 이상
- GUI 디스플레이 환경 (Windows, Mac, Linux 데스크톱)
- 최소 4GB RAM
- 1280x720 이상 해상도

## 필수 패키지

```bash
pip install opencv-python Pillow matplotlib pandas numpy
```

## 설치 및 실행

### Windows 사용자

1. **방법 1: 배치 파일 사용 (권장)**
   ```
   run_vision_cal.bat 더블클릭
   ```

2. **방법 2: 직접 실행**
   ```bash
   python Vision_Cal.py
   ```

### Mac/Linux 사용자

1. **방법 1: 실행 스크립트 사용**
   ```bash
   python3 run_vision_cal.py
   ```

2. **방법 2: 직접 실행**
   ```bash
   python3 Vision_Cal.py
   ```

### 원격 서버 실행 (SSH)

X11 forwarding을 사용하여 원격 서버에서 GUI 실행:
```bash
ssh -X username@server
cd /path/to/webapp
python3 Vision_Cal.py
```

## 프로그램 사용 방법

### 1. 프로그램 시작
- 프로그램 실행 시 사전 체크리스트 대화상자가 나타납니다
- "White balance 및 vimba setting 완료 상태 확인" 체크박스 선택
- "프로그램 시작" 버튼 클릭

### 2. 이미지 분석
1. "이미지 불러오기" 버튼으로 분석할 이미지 선택
2. 분석 방법 선택:
   - **전체 이미지 분석**: "전체 이미지 분석" 버튼 클릭
   - **영역 선택 분석**: 마우스로 영역 드래그 선택
   - **프리셋 영역**: 드롭다운에서 "기준 영역 (70,100)-(400,300)" 선택

### 3. DB 설정 최적화
- **LightStrengthGain**: 슬라이더 또는 직접 입력으로 조정
- **권장 조정값**: 목표 명도(128)에 도달하기 위한 최적값 자동 계산
- **DB 즉시 적용**: Camera XML 파일에 직접 적용

### 4. 측정 기록 관리
- **측정 결과 저장**: 현재 분석 결과를 기록에 추가
- **Excel로 내보내기**: 모든 측정 기록을 Excel 파일로 저장
- **보고서 생성**: HTML 형식의 상세 분석 보고서 생성

## 단축키
- **F1**: 사용 설명서 열기

## 문제 해결

### "no display" 오류
- GUI 환경이 아닌 곳에서 실행 시 발생
- 해결: Windows/Mac/Linux 데스크톱 환경에서 실행

### 모듈 import 오류
- 필수 패키지가 설치되지 않음
- 해결: `pip install -r requirements.txt` 실행

### Camera XML 파일 없음
- DB 파일 경로가 올바르지 않음
- 해결: C:\Park Systems\XEService\DB\Module\Vision 경로 확인

## 파일 구조

```
webapp/
├── Vision_Cal.py           # 메인 프로그램
├── run_vision_cal.py        # Python 실행 스크립트
├── run_vision_cal.bat       # Windows 배치 파일
├── test_gui.py             # 환경 테스트 스크립트
├── requirements.txt        # 필수 패키지 목록
├── report_template.html    # 보고서 템플릿
└── README.md              # 사용 설명서
```

## 개발자 정보

- **개발자**: Levi Beak / 박광림
- **소속**: Quality Assurance Team
- **이메일**: levi.beak@parksystems.com
- **버전**: 1.1.0
- **출시일**: 2025-02-04

## 라이선스

Park Systems 내부 사용 전용 소프트웨어입니다.

## 변경 이력

### v1.1.0 (2025-02-04)
- 초기 릴리즈
- 체크리스트 대화상자 추가
- 명도 분석 기능 구현
- DB 설정 최적화 기능
- 측정 기록 관리 기능
- 보고서 생성 기능