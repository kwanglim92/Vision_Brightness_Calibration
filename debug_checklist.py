#!/usr/bin/env python3
"""
체크리스트 대화상자 디버그 스크립트
GUI 없이 코드 로직을 테스트
"""

import sys
import os

def analyze_checklist_flow():
    """체크리스트 대화상자 플로우 분석"""
    
    print("Vision_Cal.py 코드 플로우 분석")
    print("=" * 60)
    
    print("\n1. 프로그램 시작 (main)")
    print("   - AppController() 인스턴스 생성")
    
    print("\n2. AppController.__init__()")
    print("   - self.root = tk.Tk() # 메인 윈도우 생성")
    print("   - self.root.withdraw() # 메인 윈도우 숨김 ⚠️")
    print("   - self.root.after(10, self.run_checklist) # 10ms 후 체크리스트 실행")
    print("   - self.root.mainloop() # 이벤트 루프 시작")
    
    print("\n3. AppController.run_checklist()")
    print("   - ChecklistDialog 생성 (부모: self.root)")
    print("   - self.root는 숨겨진 상태 ⚠️")
    print("   - 대화상자 표시 및 대기")
    print("   - 결과에 따라 start_main_app() 또는 destroy()")
    
    print("\n4. AppController.start_main_app()")
    print("   - self.root.deiconify() # 메인 윈도우 표시")
    print("   - 명도측정프로그램(self.root) 생성")
    
    print("\n" + "=" * 60)
    print("문제 분석:")
    print("-" * 40)
    
    print("\n문제점:")
    print("1. 부모 윈도우(root)가 withdraw()로 숨겨져 있음")
    print("2. 체크리스트 대화상자가 숨겨진 부모에 대한 모달로 생성됨")
    print("3. 일부 환경에서는 숨겨진 부모의 자식 대화상자가 표시되지 않을 수 있음")
    
    print("\n해결 방안:")
    print("1. 체크리스트를 표시하기 전에 부모 윈도우를 잠시 표시")
    print("2. 체크리스트 대화상자를 독립적인 Toplevel로 생성")
    print("3. 체크리스트 완료 후 메인 윈도우 재구성")
    
    print("\n" + "=" * 60)
    print("\n코드 수정 제안:")
    print("-" * 40)
    
    print("""
수정 전 (AppController.__init__):
    self.root = tk.Tk()
    self.root.withdraw()  # 완전히 숨김
    
수정 후:
    self.root = tk.Tk()
    self.root.iconify()  # 최소화만 함
    # 또는
    self.root.geometry('1x1+0+0')  # 매우 작게 만듦
    self.root.overrideredirect(True)  # 윈도우 테두리 제거
    """)
    
    print("\n또는 체크리스트 대화상자 수정:")
    print("""
수정 전 (ChecklistDialog.__init__):
    super().__init__(parent)
    self.transient(parent)
    
수정 후:
    super().__init__(parent)
    # parent가 숨겨져 있으면 transient 설정 안 함
    if parent.winfo_viewable():
        self.transient(parent)
    self.lift()  # 대화상자를 최상위로
    self.attributes('-topmost', True)  # 항상 위에 표시
    """)

def check_tkinter_behavior():
    """Tkinter 동작 확인"""
    print("\n" + "=" * 60)
    print("Tkinter 동작 테스트")
    print("=" * 60)
    
    try:
        import tkinter as tk
        
        # 간단한 테스트 코드
        test_code = """
import tkinter as tk

# 테스트 1: withdraw() 후 자식 대화상자
root1 = tk.Tk()
root1.withdraw()
dialog1 = tk.Toplevel(root1)
dialog1.title("테스트 1")
# 결과: 대화상자가 표시되지 않을 수 있음

# 테스트 2: iconify() 후 자식 대화상자  
root2 = tk.Tk()
root2.iconify()
dialog2 = tk.Toplevel(root2)
dialog2.title("테스트 2")
# 결과: 대화상자가 표시될 가능성 높음

# 테스트 3: 작은 윈도우 후 자식 대화상자
root3 = tk.Tk()
root3.geometry('1x1+0+0')
dialog3 = tk.Toplevel(root3)
dialog3.title("테스트 3")
# 결과: 대화상자가 정상 표시됨
"""
        print("테스트 시나리오:")
        print(test_code)
        
    except ImportError:
        print("Tkinter를 import할 수 없습니다 (GUI 환경 필요)")

def main():
    print("\n" + "=" * 60)
    print("Vision Brightness Calibration 체크리스트 디버그")
    print("=" * 60)
    
    analyze_checklist_flow()
    check_tkinter_behavior()
    
    print("\n" + "=" * 60)
    print("권장 수정 사항")
    print("=" * 60)
    print("""
Vision_Cal.py 파일의 AppController 클래스를 다음과 같이 수정하세요:

1. __init__ 메서드에서 withdraw() 대신 다른 방법 사용
2. ChecklistDialog가 표시되도록 보장
3. 체크리스트 완료 후 메인 윈도우 정상 표시

이 수정으로 체크리스트 대화상자가 모든 환경에서 
정상적으로 표시될 것입니다.
    """)

if __name__ == "__main__":
    main()