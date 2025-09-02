#!/usr/bin/env python3
"""
Vision Brightness Calibration 프로그램 테스트
GUI 없이 코드 구조를 테스트하는 스크립트
"""

import sys
import os

# 필요한 모듈이 있는지 확인
def check_imports():
    required_modules = [
        ('cv2', 'opencv-python'),
        ('numpy', 'numpy'),
        ('tkinter', 'python3-tk'),
        ('PIL', 'Pillow'),
        ('matplotlib', 'matplotlib'),
        ('pandas', 'pandas')
    ]
    
    missing_modules = []
    for module_name, package_name in required_modules:
        try:
            __import__(module_name)
            print(f"✓ {module_name} 모듈 정상 로드")
        except ImportError:
            print(f"✗ {module_name} 모듈 누락 (설치: pip install {package_name})")
            missing_modules.append(package_name)
    
    return missing_modules

# 코드 구조 검증
def verify_code_structure():
    """Vision_Cal.py 파일의 구조를 확인"""
    try:
        with open('Vision_Cal.py', 'r', encoding='utf-8') as f:
            code = f.read()
            
        # 주요 클래스 확인
        classes = ['ChecklistDialog', '명도측정프로그램', 'AppController']
        for cls in classes:
            if f'class {cls}' in code:
                print(f"✓ {cls} 클래스 정의됨")
            else:
                print(f"✗ {cls} 클래스 누락")
        
        # 메인 실행 부분 확인
        if 'if __name__ == "__main__":' in code:
            print("✓ 메인 실행 블록 존재")
            if 'AppController()' in code:
                print("✓ AppController 호출 확인")
        
        print("\n코드 구조 분석 완료")
        return True
        
    except Exception as e:
        print(f"코드 검증 실패: {e}")
        return False

def test_display():
    """디스플레이 환경 확인"""
    import os
    
    display = os.environ.get('DISPLAY')
    if display:
        print(f"✓ DISPLAY 환경변수 설정됨: {display}")
        return True
    else:
        print("✗ DISPLAY 환경변수 없음 - GUI 실행 불가")
        print("  해결방법:")
        print("  1. Windows/Mac/Linux 데스크톱 환경에서 실행")
        print("  2. X11 forwarding 사용 (SSH -X)")
        print("  3. VNC 서버 사용")
        print("  4. 가상 디스플레이 사용 (Xvfb)")
        return False

def main():
    print("=" * 60)
    print("Vision Brightness Calibration 프로그램 테스트")
    print("=" * 60)
    
    print("\n1. 필수 모듈 확인")
    print("-" * 40)
    missing = check_imports()
    
    print("\n2. 코드 구조 확인")
    print("-" * 40)
    verify_code_structure()
    
    print("\n3. 디스플레이 환경 확인")
    print("-" * 40)
    has_display = test_display()
    
    print("\n" + "=" * 60)
    print("테스트 결과 요약")
    print("=" * 60)
    
    if missing:
        print(f"⚠️  누락된 패키지: {', '.join(missing)}")
        print(f"   설치 명령: pip install {' '.join(missing)}")
    else:
        print("✓ 모든 필수 패키지 설치됨")
    
    if not has_display:
        print("⚠️  GUI 실행 불가 - 디스플레이 환경이 필요합니다")
        print("\n실제 사용 환경에서 실행 방법:")
        print("1. Windows/Mac/Linux 데스크톱에서 직접 실행:")
        print("   python Vision_Cal.py")
        print("\n2. 원격 서버에서 X11 forwarding으로 실행:")
        print("   ssh -X user@server")
        print("   python Vision_Cal.py")
    else:
        print("✓ GUI 실행 가능한 환경입니다")
        print("\n프로그램 실행:")
        print("   python Vision_Cal.py")
    
    print("\n" + "=" * 60)
    print("\n프로그램 동작 설명:")
    print("-" * 40)
    print("1. 프로그램 시작 시 체크리스트 대화상자가 나타납니다")
    print("2. 'White balance 및 vimba setting 완료 상태 확인' 체크")
    print("3. '프로그램 시작' 버튼 클릭")
    print("4. 메인 GUI가 표시됩니다")
    print("5. '이미지 불러오기'로 분석할 이미지 선택")
    print("6. 마우스로 영역 선택 또는 전체 이미지 분석")
    print("7. DB 설정값 조정 및 권장값 확인")
    print("8. 측정 결과 저장 및 보고서 생성")

if __name__ == "__main__":
    main()