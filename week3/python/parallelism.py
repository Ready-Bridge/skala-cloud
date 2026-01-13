# -----------------------------------------------------------------------------
# 작성자 : 한준교 (작성자명은 본인 성함으로 변경하시면 됩니다)
# 작성목적 : Python 멀티프로세싱 성능 비교
# 작성일 : 2026-01-13
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
#
# [실습 내용]
# 1. 1,000만 개의 난수 데이터 생성
# 2. 소수 판별 알고리즘 구현 (CPU 연산 집중 작업)
# 3. 단일 프로세스 vs 멀티 프로세스 처리 시간 비교
#
# [변경이력]
# 2026-01-13 : 소수 판별 헬퍼 함수 구현 (is_prime)
# 2026-01-13 : 단일/멀티 프로세스 처리 로직 및 시간 측정 기능 구현
# -----------------------------------------------------------------------------

import time
import random
import math
from multiprocessing import Pool, cpu_count

# -----------------------------------------------------------------------------
# [Data Definition]
# - 실습에 사용할 데이터 규모와 범위를 정의합니다.
# -----------------------------------------------------------------------------
DATA_SIZE = 10_000_000      # 생성할 난수의 개수 (1,000만 개)
MAX_NUMBER = 10_000_000     # 난수의 최대 범위 (1 ~ 1,000만)

# -----------------------------------------------------------------------------
# [Helper Functions]
# - 메인 비즈니스 로직에서 호출되는 단위 기능(계산) 함수입니다.
# -----------------------------------------------------------------------------

def is_prime(n):
    """
    주어진 정수가 소수(Prime Number)인지 판별하는 함수입니다.
    CPU 연산 부하를 주기 위해 의도적으로 반복문을 사용합니다.
    
    Args:
        n (int): 판별할 정수
        
    Returns:
        bool: 소수이면 True, 아니면 False
    """
    # 1과 2 미만의 수는 소수가 아님
    if n < 2:
        return False
    # 2는 소수임
    if n == 2:
        return True
    # 짝수는 소수가 아님 (2 제외)
    if n % 2 == 0:
        return False
    
    # 3부터 n의 제곱근까지 홀수만 확인하여 연산 최적화
    sqrt_n = int(math.sqrt(n))
    for i in range(3, sqrt_n + 1, 2):
        if n % i == 0:
            return False
            
    return True

# -----------------------------------------------------------------------------
# [Business Logic Functions]
# - 실제 요구사항(단일/멀티 처리)을 수행하는 핵심 함수들입니다.
# -----------------------------------------------------------------------------

def run_serial_processing(numbers):
    """
    (a) 단일 프로세스 방식으로 소수를 판별하고 시간을 측정합니다.
    
    Args:
        numbers (list): 판별할 정수 리스트
        
    Returns:
        tuple: (소수 개수(int), 소요 시간(float))
    """
    start_time = time.time()
    
    # List Comprehension를 사용하여 순차적으로 처리
    # is_prime 함수가 True를 반환하는 경우만 리스트에 남김
    primes = [n for n in numbers if is_prime(n)]
    
    count = len(primes)
    end_time = time.time()
    
    return count, end_time - start_time


def run_parallel_processing(numbers):
    """
    (b) 멀티 프로세스(Pool) 방식으로 소수를 판별하고 시간을 측정합니다.
    
    Logic:
        1. CPU 코어 수만큼 프로세스 풀(Pool)을 생성합니다.
        2. map 함수를 이용해 데이터를 여러 프로세스에 분배합니다.
        3. 각 프로세스가 병렬로 is_prime을 수행하고 결과를 합산합니다.
        
    Args:
        numbers (list): 판별할 정수 리스트
        
    Returns:
        tuple: (소수 개수(int), 소요 시간(float))
    """
    start_time = time.time()
    
    # 현재 시스템의 CPU 코어 수 확인
    num_cores = cpu_count()
    
    # Pool 객체를 사용하여 프로세스 관리 (Context Manager 사용)
    with Pool(processes=num_cores) as pool:
        # pool.map(함수, 데이터) -> 각 데이터에 함수를 적용한 결과를 리스트로 반환
        # 결과 예시: [False, True, False, ...]
        results = pool.map(is_prime, numbers)
    
    # True(=1)의 개수를 합산하여 소수 개수 계산
    count = sum(results)
    
    end_time = time.time()
    
    return count, end_time - start_time

# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print(f"--- [멀티프로세싱 성능 비교] ---")
    print(f"--- 실행 환경 : CPU {cpu_count()} Cores ---\n")

    # 1. 데이터 생성 단계
    print(f"[Step 1] {DATA_SIZE:,}개의 난수를 생성 중입니다... (잠시 대기)")
    random_numbers = [random.randint(1, MAX_NUMBER) for _ in range(DATA_SIZE)]
    print("[Step 1] 데이터 생성 완료.\n")

    # 2. 단일 프로세스 처리 (Serial)
    print("[Step 2] (a) 단일 프로세스 처리 시작...")
    serial_count, serial_time = run_serial_processing(random_numbers)
    print(f"   -> 소수 개수 : {serial_count:,} 개")
    print(f"   -> 소요 시간 : {serial_time:.4f} 초\n")

    # 3. 멀티 프로세스 처리 (Parallel)
    print("[Step 3] (b) 멀티 프로세스(Pool) 처리 시작...")
    parallel_count, parallel_time = run_parallel_processing(random_numbers)
    print(f"   -> 소수 개수 : {parallel_count:,} 개")
    print(f"   -> 소요 시간 : {parallel_time:.4f} 초\n")

    # 4. 결과 요약
    if parallel_time > 0:
        speedup = serial_time / parallel_time
        print(f"--- [결과 요약] 멀티 프로세싱이 약 {speedup:.2f}배 더 빠릅니다. ---")