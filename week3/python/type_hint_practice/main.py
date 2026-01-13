# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : Type Hint 적용 및 성능/안정성 비교 (mypy 자동 실행 포함)
# 작성일 : 2026-01-13
#
# [실습 내용]
# 1. 정수 리스트의 각 원소를 제곱하여 합산하는 함수 작성
# 2. 타입 힌트 미적용(A) vs 적용(B) 두 가지 버전 구현
# 3. mypy API를 사용하여 코드 내부에서 정적 타입 검사 수행 및 결과 출력
# 4. timeit 모듈을 사용한 실행 성능 비교 측정
#
# [변경이력]
# 2026-01-13 : 기초 데이터 생성 및 연산 함수(v1, v2) 구현
# 2026-01-13 : timeit을 이용한 벤치마킹 로직 추가
# 2026-01-13 : mypy.api를 이용한 내부 자동 검사 로직 추가
# -----------------------------------------------------------------------------

import timeit
import random
import sys
from typing import List

# mypy를 파이썬 코드 내부에서 실행하기 위한 모듈
try:
    from mypy import api
except ImportError:
    print("오류: mypy가 설치되지 않았습니다. 'pip install mypy'를 실행해주세요.")
    sys.exit(1)

# -----------------------------------------------------------------------------
# [Data Definition]
# - 실습에 사용할 데이터 규모와 범위를 정의합니다.
# -----------------------------------------------------------------------------
DATA_SIZE = 1_000_000       # 리스트 요소 개수 (100만 개)
MIN_VAL = 1                 # 난수 최소값
MAX_VAL = 100               # 난수 최대값
ITERATIONS = 10             # timeit 반복 측정 횟수

# -----------------------------------------------------------------------------
# [Business Logic Functions]
# -----------------------------------------------------------------------------

def calculate_sum_squares_no_hint(numbers):
    """
    [A 버전] 타입 힌트를 사용하지 않은 함수
    Args: numbers (타입 명시 없음)
    Returns: 결과값 (타입 명시 없음)
    """
    total = 0
    for n in numbers:
        total += n * n
    return total


def calculate_sum_squares_with_hint(numbers: List[int]) -> int:
    """
    [B 버전] 타입 힌트(Type Hint)를 적용한 함수
    Args: numbers (List[int])
    Returns: int
    """
    total: int = 0
    for n in numbers:
        total += n * n
    return total

# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"--- [A버전(타입 힌트 미적용) vs B버전(타입 힌트 적용) 비교 실습] ---\n")
    
    # 1. 데이터 생성 단계
    print(f"[Step 1] {DATA_SIZE:,}개의 정수 난수 리스트 생성 중...")
    random_numbers = [random.randint(MIN_VAL, MAX_VAL) for _ in range(DATA_SIZE)]
    print("[Step 1] 데이터 생성 완료.\n")

    # 2. mypy 자동 검사 (내부 실행)
    print("-" * 60)
    print("[Step 2] mypy 정적 타입 검사 실행 중...")
    
    # 현재 실행 중인 이 파일(__file__)을 대상으로 mypy 검사 실행
    # result_stdout: 검사 결과 메시지, result_stderr: 에러 메시지, exit_code: 상태 코드(0이면 정상)
    result_stdout, result_stderr, exit_code = api.run([__file__])
    
    if exit_code == 0:
        print(">> [PASS] 타입 검사 통과! (Success: no issues found)")
    else:
        print(">> [FAIL] 타입 검사 실패 또는 경고 발생:")
        print(result_stdout) # 어디가 틀렸는지 출력
    print("-" * 60 + "\n")

    # 3. 성능 비교 (timeit)
    print("[Step 3] timeit을 사용한 성능 비교 (반복 횟수: 10회)")
    
    # (a) 타입 힌트 없는 버전 측정
    time_no_hint = timeit.timeit(
        lambda: calculate_sum_squares_no_hint(random_numbers), 
        number=ITERATIONS
    )
    
    # (b) 타입 힌트 있는 버전 측정
    time_with_hint = timeit.timeit(
        lambda: calculate_sum_squares_with_hint(random_numbers), 
        number=ITERATIONS
    )

    # 평균 실행 시간 계산
    avg_no_hint = time_no_hint / ITERATIONS
    avg_with_hint = time_with_hint / ITERATIONS

    # 4. 결과 출력
    print(f"   (A) 타입 힌트 미적용 평균 시간 : {avg_no_hint:.5f} 초")
    print(f"   (B) 타입 힌트 적용 평균 시간   : {avg_with_hint:.5f} 초")
    
    print("\n[결과 분석]")
    if abs(avg_no_hint - avg_with_hint) < 0.05:
        print("-> 두 버전의 실행 성능은 거의 동일합니다.")
        print("   (이유: Python은 인터프리터 언어로, 타입 힌트는 런타임 성능에 영향을 주지 않습니다.)")