@echo off
REM Vision Brightness Calibration 실행 스크립트 (Windows)
REM 작성자: Levi Beak
REM 날짜: 2025-02-04

echo ============================================================
echo Vision Brightness Calibration v1.1.0
echo ============================================================
echo.

REM Python 설치 확인
python --version >nul 2>&1
if errorlevel 1 (
    echo [오류] Python이 설치되어 있지 않습니다.
    echo Python 3.8 이상을 설치해주세요: https://www.python.org/downloads/
    pause
    exit /b 1
)

echo Python 버전 확인:
python --version
echo.

REM 필수 패키지 설치
echo 필수 패키지 확인 및 설치 중...
python -m pip install --upgrade pip >nul 2>&1
python -m pip install opencv-python Pillow matplotlib pandas numpy >nul 2>&1

if errorlevel 1 (
    echo [경고] 일부 패키지 설치 실패. 수동 설치가 필요할 수 있습니다.
    echo.
)

REM 프로그램 실행
echo 프로그램을 시작합니다...
echo ------------------------------------------------------------
python Vision_Cal.py

if errorlevel 1 (
    echo.
    echo [오류] 프로그램 실행 중 문제가 발생했습니다.
    echo 오류 메시지를 확인하고 다시 시도해주세요.
) else (
    echo.
    echo 프로그램이 정상적으로 종료되었습니다.
)

echo.
pause