#!/usr/bin/env python3
"""
Vision_Cal.py 파일의 구문 오류를 수정하는 스크립트
"""

import sys
import os

def fix_syntax_errors(file_path):
    """백틱(`) 문자를 찾아서 수정"""
    
    if not os.path.exists(file_path):
        print(f"파일을 찾을 수 없습니다: {file_path}")
        return False
    
    try:
        # 파일 읽기
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # 백틱 문자 찾기 및 수정
        modified = False
        errors_found = []
        
        for i, line in enumerate(lines, 1):
            if '`' in line:
                errors_found.append(f"줄 {i}: {line.strip()}")
                # 백틱을 작은따옴표로 변경
                lines[i-1] = line.replace('`', "'")
                modified = True
        
        if errors_found:
            print("발견된 백틱(`) 오류:")
            for error in errors_found:
                print(f"  - {error}")
            
            # 백업 파일 생성
            backup_path = file_path + '.backup'
            with open(backup_path, 'w', encoding='utf-8') as f:
                with open(file_path, 'r', encoding='utf-8') as original:
                    f.write(original.read())
            print(f"\n백업 파일 생성: {backup_path}")
            
            # 수정된 내용 저장
            with open(file_path, 'w', encoding='utf-8') as f:
                f.writelines(lines)
            
            print(f"✓ 파일이 수정되었습니다: {file_path}")
            print("  백틱(`)이 작은따옴표(')로 변경되었습니다.")
            return True
        else:
            print("백틱(`) 오류를 찾을 수 없습니다.")
            
            # 754번째 줄 근처 확인
            print("\n754번째 줄 근처 내용:")
            for i in range(max(0, 753-1), min(len(lines), 756)):
                print(f"  {i+1:4d}: {lines[i].rstrip()}")
            
            return False
            
    except Exception as e:
        print(f"오류 발생: {e}")
        return False

def check_indentation(file_path):
    """들여쓰기 오류 확인"""
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            lines = f.readlines()
        
        # analyze_full_image 메소드 찾기
        in_method = False
        method_indent = None
        errors = []
        
        for i, line in enumerate(lines, 1):
            if 'def analyze_full_image(self):' in line:
                in_method = True
                method_indent = len(line) - len(line.lstrip())
                continue
            
            if in_method:
                if line.strip() and not line.strip().startswith('#'):
                    current_indent = len(line) - len(line.lstrip())
                    
                    # 메소드 종료 확인
                    if current_indent <= method_indent and 'def ' in line:
                        break
                    
                    # 들여쓰기 확인
                    if current_indent % 4 != 0:
                        errors.append(f"줄 {i}: 들여쓰기 오류 (현재: {current_indent} 공백)")
        
        if errors:
            print("\n들여쓰기 오류:")
            for error in errors:
                print(f"  - {error}")
        else:
            print("\n들여쓰기 오류가 없습니다.")
            
    except Exception as e:
        print(f"들여쓰기 확인 중 오류: {e}")

def main():
    print("=" * 60)
    print("Vision_Cal.py 구문 오류 수정 도구")
    print("=" * 60)
    
    # 파일 경로 설정
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
    else:
        # 기본 경로들 시도
        possible_paths = [
            "Vision_Cal.py",
            "./Vision_Cal.py",
            "C:/Users/Spare/Desktop/Vision Brightness Calibration/Vision_Cal.py"
        ]
        
        file_path = None
        for path in possible_paths:
            if os.path.exists(path):
                file_path = path
                break
        
        if not file_path:
            print("Vision_Cal.py 파일을 찾을 수 없습니다.")
            print("사용법: python fix_syntax_error.py <Vision_Cal.py 경로>")
            return
    
    print(f"파일 경로: {file_path}\n")
    
    # 구문 오류 수정
    if fix_syntax_errors(file_path):
        print("\n✅ 구문 오류가 수정되었습니다!")
    
    # 들여쓰기 확인
    check_indentation(file_path)
    
    print("\n" + "=" * 60)
    print("작업 완료")
    print("=" * 60)

if __name__ == "__main__":
    main()