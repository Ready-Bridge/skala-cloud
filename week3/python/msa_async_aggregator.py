import time
import asyncio
import random
from typing import Dict, List, Any, Union  # Type Hinting을 위한 모듈 추가

# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : KDT 교육용 Python 실습 목적 코드
# 작성일 : 2026-01-14
#
# 실습 목표 : 비동기 프로그래밍을 통한 서버 처리량 극대화와 실무급 보안 로직 구현
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-14 : 초기 버전 작성 (동기/비동기 API 호출 시뮬레이션 함수 구현)
# 2026-01-14 : asyncio.gather를 활용한 병렬 요청 처리 로직 추가
# 2026-01-14 : 성능 비교(Latency Measurement) 및 리포팅 기능 구현
# 2026-01-14 : [Refactor] Python Type Hinting(typing) 전면 적용
# 2026-01-14 : [Security] 로그 마스킹(Masking) 및 요청 헤더 인증(Auth Check) 로직 추가
# 2026-01-14 : [Refactor] Sync/Async 공통 보안 및 로깅 로직 추출 (Pre-process 통합)
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# [Security Note]
# 실제 운영 환경에서는 클라이언트(웹/앱)가 실수로 토큰을 누락하거나,
# 해커가 비인가 요청을 보낼 수 있습니다.
# 따라서 비즈니스 로직(DB 조회 등)을 수행하기 전에, 
# 가장 먼저 인증 여부를 검사(Fail-Fast)해야 리소스 낭비를 막을 수 있습니다.
# 본 실습 코드에서는 간단히 토큰 일치 여부만 확인하지만,
# 실제로는 OAuth2, JWT, API Key 등 다양한 인증 방식을 적용해야 합니다
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# [Data Definition & Configuration]
# - 실습을 위한 가상의 마이크로서비스 엔드포인트와 예상 응답 지연시간(Latency) 정의입니다.
# -----------------------------------------------------------------------------

# MSA 서비스 목록 (서비스명: 예상 소요 시간 초)
MICROSERVICES_CONFIG: Dict[str, float] = {
    "Auth_Service": 0.5,      # 인증 토큰 검증 (0.5초)
    "User_Profile_API": 1.0,  # 사용자 기본 정보 조회 (1.0초)
    "Order_History_API": 2.0, # 주문 이력 조회 (2.0초 -> 가장 느린 서비스)
    "Product_Rec_API": 1.5,   # 추천 상품 분석 (1.5초)
}

# [Security] API 접근을 위한 가상의 비밀키 (절대 코드에 하드코딩해서 커밋하면 안 되지만, 실습용으로 정의)
API_SECRET_KEY: str = "skala cloud fighting!"

# -----------------------------------------------------------------------------
# [Helper Functions]
# - 로깅, 시간 측정 등 메인 비즈니스 로직을 보조하는 유틸리티 함수들입니다.
# -----------------------------------------------------------------------------

def mask_secret(text: str) -> str:
    """
    [Security] 로그에 민감한 정보(토큰 등)가 그대로 남지 않도록 마스킹 처리합니다.
    앞 4자리만 보여주고 나머지는 '*'로 처리합니다.
    
    Args:
        text (str): 원본 문자열
        
    Returns:
        str: 마스킹된 문자열
    """
    if len(text) <= 4:
        return "****"
    return text[:4] + "*" * (len(text) - 4)


def print_log(message: str) -> None:
    """
    현재 실행 시간과 함께 로그 메시지를 출력합니다.
    
    Args:
        message (str): 출력할 메시지 본문
    """
    current_time = time.strftime("%H:%M:%S", time.localtime())
    print(f"[{current_time}] {message}")


def simulate_processing(service_name: str, delay: float) -> str:
    """
    서비스 처리 시간을 시뮬레이션하는 메시지 생성 헬퍼입니다.
    
    Args:
        service_name (str): 서비스 이름
        delay (float): 지연 시간
    
    Returns:
        str: 완료 메시지
    """
    return f"{service_name} 처리 완료 (소요시간: {delay}s)"

# -----------------------------------------------------------------------------
# [Security Logic Functions]
# - API Gateway 또는 서비스 진입점에서 수행할 보안 검증 로직입니다.
# -----------------------------------------------------------------------------

def validate_request_header(headers: Dict[str, str]) -> bool:
    """
    [Security] 요청 헤더에 유효한 인증 토큰이 있는지 검증합니다.
    
    Args:
        headers (Dict[str, str]): HTTP 요청 헤더
        
    Returns:
        bool: 인증 성공 여부 (True/False)
    """
    # Authorization 헤더 존재 여부 및 값 검증
    token = headers.get("Authorization", "")
    
    # "Bearer " 접두어 제거 및 키 비교
    # 키에 공백이 포함되어 있으므로 split(" ", 1)을 사용하여 첫 번째 공백에서만 자릅니다.
    if token.startswith("Bearer ") and token.split(" ", 1)[1] == API_SECRET_KEY:
        return True
    return False


def pre_process_request(mode: str, service_name: str, headers: Dict[str, str]) -> bool:
    """
    [Security] 공통 보안 검증 및 로깅 수행 (DRY 원칙 적용)
    
    Args:
        mode (str): 호출 모드 (Sync/Async)
        service_name (str): 서비스 이름
        headers (Dict[str, str]): HTTP 요청 헤더
        
    Returns:
        bool: 검증 통과 여부
    """
    if not validate_request_header(headers):
        print_log(f"[{mode}][Security] '{service_name}' 접근 거부 (Invalid Token)")
        return False

    masked_token = mask_secret(headers.get("Authorization", "").replace("Bearer ", ""))
    msg_suffix = "대기" if mode == "Sync" else "전송"
    print_log(f"[{mode}] '{service_name}' 요청 {msg_suffix} (Token: {masked_token})...")
    return True

# -----------------------------------------------------------------------------
# [Business Logic Functions - Synchronous]
# - 기존 레거시 시스템 방식의 차단(Blocking) I/O 로직입니다.
# -----------------------------------------------------------------------------

def fetch_data_sync(service_name: str, base_delay: float, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    동기(Blocking) 방식으로 외부 API 데이터를 가져오는 함수입니다.
    보안 검증 후 time.sleep()을 사용하여 대기합니다.

    Args:
        service_name (str): 호출할 마이크로서비스 이름
        base_delay (float): 서비스의 기본 응답 지연 시간
        headers (Dict[str, str]): 인증 정보가 담긴 헤더

    Returns:
        Dict[str, Any]: {서비스명: 결과데이터, 상태: 성공/실패}
    """
    # 1. 보안 검증 및 공통 처리 (Refactored)
    if not pre_process_request("Sync", service_name, headers):
        return {"service": service_name, "status": "401 Unauthorized", "data": None}
    
    # 2. [Blocking I/O Simulation]
    time.sleep(base_delay)
    
    result_msg = simulate_processing(service_name, base_delay)
    print_log(f"[Sync] '{service_name}' 응답 수신 완료.")
    
    return {"service": service_name, "status": "200 OK", "data": result_msg}


def execute_sequential_aggregation() -> float:
    """
    모든 마이크로서비스를 '순차적(Sequential)'으로 호출하여 데이터를 취합합니다.
    
    Returns:
        float: 총 수행 시간(초)
    """
    print("\n>>> 1. 동기(Synchronous) 방식 실행 시작 (순차 처리 + 보안 검증)")
    
    # [Security] 요청 헤더 생성
    headers = {"Authorization": f"Bearer {API_SECRET_KEY}"}
    
    start_time = time.perf_counter()
    
    results: List[Dict[str, Any]] = []
    
    for service, delay in MICROSERVICES_CONFIG.items():
        data = fetch_data_sync(service, delay, headers)
        results.append(data)
        
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f">>> 동기 방식 결과 취합 완료: {len(results)}건")
    return duration

# -----------------------------------------------------------------------------
# [Business Logic Functions - Asynchronous]
# - asyncio를 활용한 비차단(Non-blocking) I/O 로직입니다.
# -----------------------------------------------------------------------------

async def fetch_data_async(service_name: str, base_delay: float, headers: Dict[str, str]) -> Dict[str, Any]:
    """
    비동기(Non-blocking) 방식으로 외부 API 데이터를 가져오는 Coroutine입니다.
    보안 검증 로직은 CPU 연산이므로 동기적으로 처리되지만, I/O 대기는 비동기로 처리됩니다.

    Args:
        service_name (str): 호출할 마이크로서비스 이름
        base_delay (float): 서비스의 기본 응답 지연 시간
        headers (Dict[str, str]): 인증 정보가 담긴 헤더

    Returns:
        Dict[str, Any]: {서비스명: 결과데이터, 상태: 성공/실패}
    """
    # 1. 보안 검증 및 공통 처리 (Refactored)
    if not pre_process_request("Async", service_name, headers):
        return {"service": service_name, "status": "401 Unauthorized", "data": None}
    
    # 2. [Non-blocking I/O Simulation]
    await asyncio.sleep(base_delay)
    
    result_msg = simulate_processing(service_name, base_delay)
    print_log(f"[Async] '{service_name}' 데이터 수신 확인.")
    
    return {"service": service_name, "status": "200 OK", "data": result_msg}


async def execute_concurrent_aggregation() -> float:
    """
    모든 마이크로서비스를 '병렬(Concurrent)'로 호출하여 데이터를 취합합니다.
    
    Logic:
        1. 각 서비스별 Coroutine 객체(Task)를 생성합니다.
        2. asyncio.gather()를 통해 모든 Task를 동시에 스케줄링합니다.
        
    Returns:
        float: 총 수행 시간(초)
    """
    print("\n>>> 2. 비동기(Asynchronous) 방식 실행 시작 (병렬 처리 + 보안 검증)")
    
    # [Security] 요청 헤더 생성
    headers = {"Authorization": f"Bearer {API_SECRET_KEY}"}
    
    start_time = time.perf_counter()
    
    # 1. 실행할 코루틴(Task) 리스트 생성
    futures = [
        fetch_data_async(service, delay, headers) 
        for service, delay in MICROSERVICES_CONFIG.items()
    ]
    
    # 2. asyncio.gather로 동시 실행 및 결과 대기
    results = await asyncio.gather(*futures)
    
    end_time = time.perf_counter()
    duration = end_time - start_time
    
    print(f">>> 비동기 방식 결과 취합 완료: {len(results)}건")
    return duration

# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------

def main() -> None:
    print("--- [MSA API Aggregator 성능 비교 및 보안 실습] ---\n")
    print(f"대상 서비스 목록: {list(MICROSERVICES_CONFIG.keys())}")
    
    # 1. 동기 방식 실행 (Sequential)
    sync_duration = execute_sequential_aggregation()
    print(f"동기 방식 총 소요 시간: {sync_duration:.4f}초")
    
    print("-" * 60)
    
    # 2. 비동기 방식 실행 (Concurrent)
    async_duration = asyncio.run(execute_concurrent_aggregation())
    print(f"비동기 방식 총 소요 시간: {async_duration:.4f}초")
    
    print("-" * 60)
    
    # 3. 결과 분석 및 리포트
    print("\n--- [Performance Report] ---")
    print(f"1. Sync  Time : {sync_duration:.4f}s (직렬 합계)")
    print(f"2. Async Time : {async_duration:.4f}s (최대 지연 시간 근사)")
    
    if async_duration > 0:
        improvement = sync_duration / async_duration
        print(f"성능 향상 배수: 약 {improvement:.2f}배 더 빠름")
    
    print("\n[최종 결론]")
    print(f"{len(MICROSERVICES_CONFIG)}개의 서비스를 순차 대기하지 않고 '동시 처리'하여, 전체 응답 시간을 [모든 지연시간의 합]에서 [가장 느린 서비스의 시간]으로 단축함.")

if __name__ == "__main__":
    main()