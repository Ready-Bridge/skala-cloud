# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : 데코레이터로 함수 실행시간 측정기 구현
# 작성일 : 2026-01-13
#
# 본 파일은 KDT 교육을 위한 실습 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-13 : 함수 실행 시간 측정 데코레이터(measure_time) 구현
# 2026-01-13 : 테스트용 느린 함수(slow_function) 작성
# 2026-01-13 : 메인 실행부에서 데코레이터 적용 함수 실행 및 결과 출력
# -----------------------------------------------------------------------------

import time
from functools import wraps

def measure_time(func):
    """
    함수의 실행 시간을 측정하여 출력하는 데코레이터
    """
    @wraps(func)  # 원본 함수의 이름을 보존
    def wrapper(*args, **kwargs):
        # 1. 시작 시간 기록
        start_time = time.time()
        
        # 2. 원본 함수 실행 및 결과 저장
        result = func(*args, **kwargs)
        
        # 3. 종료 시간 기록 및 소요 시간 계산
        end_time = time.time()
        execution_time = end_time - start_time
        
        # 4. 실행 시간 출력 (소수점 4자리까지)
        print(f"{func.__name__} took {execution_time:.4f} seconds")
        
        # 5. 원본 함수의 실행 결과 반환
        return result
    
    return wrapper

@measure_time
def slow_function(seconds):
    """
    지정된 시간만큼 대기하는 테스트 함수
    """
    print(f"{seconds} 초 대기...")
    time.sleep(seconds)
    return "Finished"

# --- 실행부 ---
if __name__ == "__main__":
    # 임의의 연산 지연(2초)을 주어 실행 확인
    output = slow_function(2)
    print(f"함수 실행 결과: {output}")