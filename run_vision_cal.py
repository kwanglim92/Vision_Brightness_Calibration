#!/usr/bin/env python3
"""
Vision Brightness Calibration 실행 스크립트
GUI 환경에서 프로그램을 실행하기 위한 래퍼 스크립트
"""

import sys
import os
import subprocess
import platform

def check_display():
    """디스플레이 환경 확인"""
    if platform.system() == 'Windows':
        # Windows는 항상 디스플레이가 있다고 가정
        return True
    else:
        # Unix/Linux/Mac에서 DISPLAY 환경변수 확인
        return os.environ.get('DISPLAY') is not None

def install_missing_packages():
    """누락된 패키지 자동 설치"""
    required_packages = {
        'cv2': 'opencv-python',
        'PIL': 'Pillow',
        'matplotlib': 'matplotlib',
        'pandas': 'pandas',
        'numpy': 'numpy'
    }
    
    for module, package in required_packages.items():
        try:
            __import__(module)
        except ImportError:
            print(f"Installing {package}...")
            subprocess.check_call([sys.executable, '-m', 'pip', 'install', package])

def run_program():
    """메인 프로그램 실행"""
    try:
        # Vision_Cal.py 직접 실행
        import Vision_Cal
    except Exception as e:
        print(f"프로그램 실행 중 오류 발생: {e}")
        return False
    return True

def main():
    print("=" * 60)
    print("Vision Brightness Calibration v1.1.0")
    print("=" * 60)
    
    # 디스플레이 확인
    if not check_display():
        print("\n⚠️  경고: GUI 디스플레이를 찾을 수 없습니다.")
        print("이 프로그램은 GUI 환경에서만 실행 가능합니다.")
        print("\n실행 방법:")
        print("1. Windows/Mac/Linux 데스크톱 환경에서 실행")
        print("2. SSH에서 X11 forwarding 사용 (ssh -X)")
        print("3. VNC 또는 원격 데스크톱 사용")
        
        response = input("\n그래도 실행하시겠습니까? (y/n): ")
        if response.lower() != 'y':
            print("프로그램을 종료합니다.")
            sys.exit(0)
    
    print("\n필수 패키지 확인 중...")
    try:
        install_missing_packages()
        print("✓ 모든 필수 패키지가 준비되었습니다.")
    except Exception as e:
        print(f"✗ 패키지 설치 실패: {e}")
        print("수동으로 다음 명령을 실행해주세요:")
        print("pip install opencv-python Pillow matplotlib pandas numpy")
        sys.exit(1)
    
    print("\n프로그램을 시작합니다...")
    print("-" * 60)
    
    if run_program():
        print("\n프로그램이 정상적으로 종료되었습니다.")
    else:
        print("\n프로그램 실행 중 문제가 발생했습니다.")
        print("Vision_Cal.py 파일을 직접 실행해보세요:")
        print("  python Vision_Cal.py")

if __name__ == "__main__":
    main()