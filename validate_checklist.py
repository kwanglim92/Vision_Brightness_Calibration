"""
체크리스트 다이얼로그 코드 검증 스크립트
GUI 없이도 실행 가능한 validation
"""

import ast
import sys


def validate_python_syntax(file_path):
    """Python 파일의 구문을 검증"""
    print(f"\n검증 중: {file_path}")
    print("-" * 60)

    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            source_code = f.read()

        # AST 파싱으로 구문 검증
        tree = ast.parse(source_code)
        print("✓ 구문 검증 통과")

        # 클래스 및 메서드 분석
        classes = [node for node in ast.walk(tree) if isinstance(node, ast.ClassDef)]
        functions = [node for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        print(f"✓ 클래스 수: {len(classes)}")
        for cls in classes:
            print(f"  - {cls.name}")

        print(f"✓ 함수/메서드 수: {len(functions)}")

        # 주요 메서드 확인
        required_methods = [
            '_configure_styles',
            '_initialize_tooltips',
            '_update_progress',
            '_update_progress_color',
            '_update_category_status',
            '_update_checkbox_styles',
            '_on_check_changed'
        ]

        function_names = [f.name for f in functions]
        print("\n주요 메서드 존재 확인:")
        for method in required_methods:
            if method in function_names:
                print(f"  ✓ {method}")
            else:
                print(f"  ✗ {method} (누락)")
                return False

        # COLORS 상수 확인
        if 'COLORS' in source_code:
            print("\n✓ COLORS 상수 정의됨")

            # 필요한 색상 키 확인
            required_colors = ['success', 'warning', 'danger', 'info', 'neutral',
                             'text_completed', 'text_important', 'bg_tooltip']
            for color in required_colors:
                if f"'{color}'" in source_code:
                    print(f"  ✓ {color}")

        # ToolTip 클래스 확인
        tooltip_class = next((cls for cls in classes if cls.name == 'ToolTip'), None)
        if tooltip_class:
            print("\n✓ ToolTip 클래스 정의됨")
        else:
            print("\n✗ ToolTip 클래스 누락")
            return False

        print("\n" + "=" * 60)
        print("모든 검증 통과! ✓")
        print("=" * 60)
        return True

    except SyntaxError as e:
        print(f"✗ 구문 오류: {e}")
        return False
    except Exception as e:
        print(f"✗ 검증 실패: {e}")
        return False


def check_improvements():
    """개선 사항 요약"""
    print("\n" + "=" * 60)
    print("체크리스트 UI 개선 사항 요약")
    print("=" * 60)

    improvements = [
        ("진행률 표시", "전체 진행률 바 및 퍼센트 표시 추가"),
        ("카테고리 상태", "✓/⚠/○ 아이콘 및 [X/Y] 진행률 표시"),
        ("색상 코딩", "완료(초록), 진행중(파랑), 미완료(회색) 구분"),
        ("시각적 피드백", "체크된 항목 회색 텍스트, 중요 항목 빨간색"),
        ("툴팁", "모든 항목에 마우스 오버 시 상세 설명 표시"),
        ("버튼 UX", "남은 항목 수 동적 표시, 완료 시 체크 아이콘"),
        ("레이아웃", "윈도우 크기 850x680, 여백 및 패딩 최적화"),
    ]

    for i, (title, desc) in enumerate(improvements, 1):
        print(f"{i}. {title:15s} : {desc}")

    print("=" * 60)


if __name__ == "__main__":
    print("=" * 60)
    print("체크리스트 다이얼로그 코드 검증")
    print("=" * 60)

    file_path = "src/gui/checklist_dialog.py"

    if validate_python_syntax(file_path):
        check_improvements()
        sys.exit(0)
    else:
        print("\n검증 실패!")
        sys.exit(1)
