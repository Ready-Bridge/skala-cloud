"""
--------------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : 대용량 데이터(1,000만 건) 처리 시 List와 Generator의 메모리 효율성 비교
# 작성일 : 2026-01-12
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-12 : 초기 템플릿 작성 및 환경 구성
# 2025-01-12 : 100만 개 정수 리스트 생성 및 메모리 측정 로직 구현
# 2025-01-12 : yield 키워드를 활용한 제너레이터 함수 구현 및 성능 비교 로직 추가

# 2026-01-12 : 데이터 처리량을 1,000만 개(10,000,000)로 상향 조정
# 2026-01-12 : 정확한 메모리 피크(Peak) 측정을 위해 tracemalloc 모듈 도입
# 2026-01-12 : 결과 분석을 통한 Lazy Evaluation(지연 평가) 설명 로직 구현
--------------------------------------------------------------------------------
"""

# [Imports] 시스템 및 메모리 추적 관련 모듈
import sys
import tracemalloc
import time

# -----------------------------------------------------------------------------
# [Data Definition]
# - 전역 변수, 상수(Constants), 실습용 데이터셋 등을 정의하는 구역입니다.
# -----------------------------------------------------------------------------
TARGET_COUNT = 10_000_001 # 처리할 데이터 개수 (1,000만 개)


# -----------------------------------------------------------------------------
# [Helper Functions]
# - 메인 로직을 보조하는 단순 기능, 포맷팅, 유틸리티 함수들을 정의합니다.
# -----------------------------------------------------------------------------

def print_section_title(title):
    """
    출력 결과의 가독성을 높이기 위해 섹션 제목을 구분선과 함께 출력합니다.

    Args:
        title (str): 출력할 섹션의 제목

    Returns:
        None
    """
    print(f"\n" + "="*60)
    print(f" [Step] {title}")
    print("="*60)


def format_bytes(size):
    """
    바이트(Bytes) 단위의 숫자를 읽기 쉬운 문자열로 변환합니다.
    정확한 비교를 위해 Bytes와 MB 단위를 병기합니다.

    Args:
        size (int): 변환할 바이트 크기

    Returns:
        str: "xxx,xxx Bytes (xx.xx MB)" 형태의 문자열
    """
    # 1 MB = 1024 * 1024 bytes
    power = 1024 * 1024
    n = size / power
    return f"{size:,} Bytes ({n:.2f} MB)"


def measure_memory_and_execute(func, *args):
    """
    함수 실행 중 발생하는 메모리 사용량의 최고점(Peak)을 측정합니다.
    tracemalloc을 사용하여 시작과 종료 사이의 메모리 변화를 추적합니다.

    Args:
        func (callable): 실행할 함수 객체
        *args: 함수에 전달할 가변 인자

    Returns:
        tuple: (함수의 실행 결과, 측정된 최대 메모리 사용량(bytes), 소요 시간(seconds))
    """
    # 1. 메모리 추적 시작
    tracemalloc.start()
    start_time = time.time()

    # 2. 실제 함수 실행
    result = func(*args)

    # 3. 메모리 및 시간 측정 종료
    end_time = time.time()
    _, peak = tracemalloc.get_traced_memory() # (current, peak) 중 peak만 가져옴
    tracemalloc.stop()

    execution_time = end_time - start_time
    return result, peak, execution_time


# -----------------------------------------------------------------------------
# [Business Logic Functions]
# - 실제 요구사항을 처리하는 핵심 알고리즘 및 데이터 처리 함수들을 정의합니다.
# -----------------------------------------------------------------------------

def use_list_comprehension(n):
    """
    List Comprehension을 사용하여 0부터 n-1까지의 데이터를 
    메모리에 즉시 생성(Eager Evaluation)하고 합계를 구합니다.

    Args:
        n (int): 생성할 숫자의 개수

    Returns:
        int: 리스트 요소들의 총합
    """
    # [주의] n개의 정수를 가진 거대한 리스트가 메모리에 한 번에 할당됩니다.
    data_list = [i for i in range(n)]
    return sum(data_list)


def use_generator_expression(n):
    """
    Generator Expression을 사용하여 0부터 n-1까지의 데이터를
    필요할 때마다 하나씩 생성(Lazy Evaluation)하며 합계를 구합니다.

    Args:
        n (int): 생성할 숫자의 개수

    Returns:
        int: 제너레이터 요소들의 총합
    """
    # [특징] 데이터를 담을 메모리 공간을 미리 만들지 않고, 생성 규칙만 정의합니다.
    # 소괄호 ()를 사용하면 제너레이터 표현식이 됩니다.
    data_gen = (i for i in range(n))
    return sum(data_gen)


# -----------------------------------------------------------------------------
# [Main Execution Flow]
# - 스크립트 실행 시 수행되는 메인 진입점(Entry Point)입니다.
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f">>> 프로그램 실행 시작 (처리 데이터: {TARGET_COUNT - 1:,}개)")

    # ---------------------------------------------------------
    # 1. 일반 리스트(List) 방식 실습 (Eager Evaluation)
    # ---------------------------------------------------------
    print_section_title("1. List Comprehension (즉시 평가) 측정")
    
    list_result, list_peak, list_time = measure_memory_and_execute(use_list_comprehension, TARGET_COUNT)
    
    print(f" -> 결과 값      : {list_result:,}")
    print(f" -> 소요 시간    : {list_time:.4f} sec")
    print(f" -> Peak Memory : {format_bytes(list_peak)}")


    # ---------------------------------------------------------
    # 2. 제너레이터(Generator) 방식 실습 (Lazy Evaluation)
    # ---------------------------------------------------------
    print_section_title("2. Generator Expression (지연 평가) 측정")

    gen_result, gen_peak, gen_time = measure_memory_and_execute(use_generator_expression, TARGET_COUNT)

    print(f" -> 결과 값      : {gen_result:,}")
    print(f" -> 소요 시간    : {gen_time:.4f} sec")
    print(f" -> Peak Memory : {format_bytes(gen_peak)}")


    # ---------------------------------------------------------
    # 3. 결과 비교 및 원리 설명 (Lazy Evaluation)
    # ---------------------------------------------------------
    print_section_title("3. 최종 비교 및 Lazy Evaluation 원리 분석")

    # 메모리 절감 배수 계산
    ratio = list_peak / gen_peak if gen_peak > 0 else 0
    # 속도 차이 계산
    speed_factor = list_time / gen_time if gen_time > 0 else 0
        
    print(f"[실측 데이터 검증]")
    print(f" - 데이터 일치 여부 : {list_result == gen_result} (동일 합계)")
    print(f" - 메모리 효율성    : 제너레이터가 약 [{ratio:,.1f}배] 더 적은 메모리 사용")
    print(f" - 처리 속도 참고   : 제너레이터가 약 [{speed_factor:.2f}배] 더 빠르게 측정됨\n")

    print("[핵심 분석: 왜 제너레이터가 압도적으로 유리할까?]")
    print("-" * 60)
    print("1. 메모리 점유 방식의 차이")
    print("   - 리스트: 1,000만 개 데이터를 메모리에 '미리' 다 올려야만 연산을 시작함.")
    print("   - 제너레이터: 데이터를 미리 만들지 않고, 필요할 때 '하나씩'만 생성함.")
    print("   => 이 과정에서 리스트는 수백 MB의 메모리를 점유하지만, 제너레이터는 바이트 단위만 사용.")
    print("")
    print("2. 왜 속도까지 빠르게 측정되었나?")
    print("   - 리스트가 1,000만 개의 정수 객체를 생성하고 메모리 공간을 확보하는 동안,")
    print("   - 제너레이터는 그런 '준비 과정' 없이 즉시 계산을 시작하기 때문입니다.")
    print("   - 즉, '데이터 생성 + 계산'이 결합된 작업에서는 제너레이터가 더 효율적입니다.")
    print("-" * 60)
    
    print("\n[상황별 선택 가이드]")
    print(" - 리스트: 이미 저장된 데이터를 여러 번 다시 쓰거나, 임의의 위치(data[i])를 읽어야 할 때")
    print(" - 제너레이터: 이번 실습처럼 '한 번 읽고 끝내는 대용량 데이터'를 처리할 때 (필수 선택)")

    print(f"\n>>> 프로그램 실행 종료")