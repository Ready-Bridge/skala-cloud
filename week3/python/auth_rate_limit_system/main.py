import time
import bcrypt
import math
from typing import Dict, Tuple, Optional, Any

# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : KDT 교육용 Python 실습 목적 코드
# 작성일 : 2026-01-14
#
# 실습 목표 : Bcrypt 해시 기반의 보안 인증 및 Rate Limiting(속도 제한) 시스템 구현
#
# 본 파일은 KDT 교육을 위한 실습 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-14 : 초기 버전 작성 (Bcrypt 해시 생성 및 검증 로직 구현)
# 2026-01-14 : In-Memory 기반 IP별 로그인 실패 횟수 추적 기능 추가
# 2026-01-14 : 지수 백오프(Exponential Backoff) 알고리즘 적용 (무차별 대입 방어)
# 2026-01-14 : PII(개인정보) 보호를 위한 로깅 마스킹 처리 유틸리티 추가
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# [Configuration]
# - 보안 정책 및 임계값 설정
# -----------------------------------------------------------------------------
MAX_RETRIES: int = 3         # 허용된 최대 연속 실패 횟수
BASE_DELAY: float = 2.0      # 백오프 시작 시간 (초) -> 2초, 4초, 8초... 지수적으로 증가
BCRYPT_ROUNDS: int = 12      # Bcrypt 비용 계수 -> 사용자 로그인 시 서버가 느끼는 부담이 적절한 지점. (약 0.2~0.3초 소요)

# -----------------------------------------------------------------------------
# [Data Definition]
# - 인메모리 저장소 정의
# -----------------------------------------------------------------------------

# 사용자 DB 시뮬레이션 (Username: Hashed_Password)
# 실제 환경에서는 DB에서 조회해야 함
USER_DB: Dict[str, bytes] = {}

# IP별 실패 이력 저장소
# Key: IP Address (str)
# Value: {"count": 실패횟수, "last_attempt": 마지막시도시간(timestamp)}
LOGIN_ATTEMPTS: Dict[str, Dict[str, Any]] = {}

# -----------------------------------------------------------------------------
# [Helper Functions]
# -----------------------------------------------------------------------------

def mask_ip(ip_address: str) -> str:
    """
    [Security] 로그 출력 시 IP 주소의 일부를 마스킹하여 개인정보를 보호합니다.
    IPv4 기준 마지막 옥텟을 마스킹합니다. (예: 192.168.0.1 -> 192.168.0.***)

    Args:
        ip_address (str): 원본 IP 주소

    Returns:
        str: 마스킹된 IP 주소
    """
    parts = ip_address.split('.')
    if len(parts) == 4:
        return f"{parts[0]}.{parts[1]}.{parts[2]}.***"
    return ip_address


def print_log(level: str, message: str) -> None:
    """
    표준화된 로그 포맷을 출력합니다.
    
    Args:
        level (str): 로그 레벨 (INFO, WARN, ERROR)
        message (str): 로그 메시지
    """
    current_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())
    print(f"[{current_time}] [{level}] {message}")


def register_user(username: str, password: str) -> None:
    """
    신규 사용자를 등록합니다. 비밀번호는 Bcrypt로 단방향 해싱되어 저장됩니다.
    
    Args:
        username (str): 사용자 아이디
        password (str): 평문 비밀번호
    """
    # salt 생성 및 해싱 (CPU Bound 작업)
    salt = bcrypt.gensalt(rounds=BCRYPT_ROUNDS)
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), salt)
    
    USER_DB[username] = hashed_pw
    print_log("INFO", f"사용자 등록 완료: {username} (Hash Length: {len(hashed_pw)})")


# -----------------------------------------------------------------------------
# [Core Security Logic Functions]
# -----------------------------------------------------------------------------

def check_rate_limit_policy(ip_address: str) -> Tuple[bool, float]:
    """
    해당 IP의 로그인 시도 가능 여부를 판단합니다.
    지수 백오프(Exponential Backoff) 알고리즘을 적용하여,
    실패 횟수가 많을수록 대기 시간을 2의 지수승으로 증가시킵니다.

    Args:
        ip_address (str): 요청 IP 주소

    Returns:
        Tuple[bool, float]: (허용여부, 남은대기시간)
    """
    # 이력이 없으면 통과
    if ip_address not in LOGIN_ATTEMPTS:
        return True, 0.0

    record = LOGIN_ATTEMPTS[ip_address]
    fail_count = record["count"]
    last_attempt = record["last_attempt"]

    # 임계값 이하의 실패는 허용
    if fail_count < MAX_RETRIES:
        return True, 0.0

    # 지수 백오프 대기 시간 계산: Base_Delay * 2^(초과횟수)
    # 예: 3회 실패 시점 -> 2 * 2^0 = 2초 대기
    # 예: 4회 실패 시점 -> 2 * 2^1 = 4초 대기
    exponent = fail_count - MAX_RETRIES
    required_wait_time = BASE_DELAY * (2 ** exponent)
    
    elapsed_time = time.time() - last_attempt

    if elapsed_time < required_wait_time:
        return False, (required_wait_time - elapsed_time)
    
    return True, 0.0


def record_login_failure(ip_address: str) -> None:
    """
    로그인 실패 시 해당 IP의 실패 카운트를 증가시키고 타임스탬프를 갱신합니다.

    Args:
        ip_address (str): 요청 IP 주소
    """
    current_time = time.time()
    
    if ip_address not in LOGIN_ATTEMPTS:
        LOGIN_ATTEMPTS[ip_address] = {"count": 1, "last_attempt": current_time}
    else:
        LOGIN_ATTEMPTS[ip_address]["count"] += 1
        LOGIN_ATTEMPTS[ip_address]["last_attempt"] = current_time
        
    fail_count = LOGIN_ATTEMPTS[ip_address]["count"]
    masked_ip = mask_ip(ip_address)
    print_log("WARN", f"로그인 실패 감지 (IP: {masked_ip}, 누적 실패: {fail_count}회)")


def reset_login_failure(ip_address: str) -> None:
    """
    로그인 성공 시 해당 IP의 실패 기록을 초기화합니다.
    
    Args:
        ip_address (str): 요청 IP 주소
    """
    if ip_address in LOGIN_ATTEMPTS:
        del LOGIN_ATTEMPTS[ip_address] # 파이썬 예약어로 삭제(빠르고 간단함)
        masked_ip = mask_ip(ip_address)
        print_log("INFO", f"로그인 성공으로 보안 정책 초기화 (IP: {masked_ip})")


def authenticate_user(username: str, password: str, ip_address: str) -> bool:
    """
    사용자 인증 메인 파이프라인입니다.
    Rate Limiting 검사 -> DB 조회 -> Bcrypt 검증 순으로 수행됩니다.

    Args:
        username (str): 아이디
        password (str): 패스워드
        ip_address (str): 요청자 IP

    Returns:
        bool: 로그인 성공 여부
    """
    masked_ip = mask_ip(ip_address)

    # 1. Rate Limiting 검사 (In-Memory Check)
    is_allowed, wait_time = check_rate_limit_policy(ip_address)
    if not is_allowed:
        print_log("ERROR", f"요청 차단됨 (IP: {masked_ip}) - 지수 백오프 적용 중: {wait_time:.2f}초 대기 필요")
        return False

    # 2. 사용자 존재 여부 확인
    if username not in USER_DB:
        # 보안상 아이디가 틀렸는지 비밀번호가 틀렸는지 알려주지 않음 (로그로만 남김)
        record_login_failure(ip_address)
        print_log("WARN", f"인증 실패: 사용자 정보 없음 (User: {username})")
        return False

    stored_hash = USER_DB[username]

    # 3. Bcrypt 비밀번호 검증 (CPU Intensive)
    # checkpw는 내부적으로 해시 연산을 수행하므로 시간이 소요됨
    try:
        is_valid = bcrypt.checkpw(password.encode('utf-8'), stored_hash)
    except Exception as e:
        print_log("ERROR", f"시스템 오류 발생: {str(e)}")
        return False

    if is_valid:
        reset_login_failure(ip_address)
        print_log("INFO", f"인증 성공 (User: {username}, IP: {masked_ip})")
        return True
    else:
        record_login_failure(ip_address)
        print_log("WARN", f"인증 실패: 비밀번호 불일치 (User: {username})")
        return False


# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------

def main() -> None:
    print("--- [Bcrypt 기반 Rate Limiting 인증 시스템 실습] ---\n")
    
    # 1. 테스트 사용자 등록
    target_user = "skala-cloud-hanjungyo"
    register_user(target_user, "secure_password_123")
    
    # 2. 공격 시나리오 설정을 위한 가상 해커 IP 정의
    attacker_ip = "203.0.113.45"  # 예시 IP
    
    print("\n>>> 시나리오 1: 무차별 대입 공격 시뮬레이션 시작")
    print(f"정책: {MAX_RETRIES}회 실패 시 {BASE_DELAY}초부터 지수적으로 대기 시간 증가\n")

    # 공격 시도 (총 6회 시도)
    passwords_to_try = [
        "1234", "qwerty", "admin", "password",  # 4회 실패 유도
        "secure_password_123",                  # 5회차에 정답 시도 (하지만 차단되어야 함)
        "secure_password_123"                   # 6회차에 대기 후 재시도 (성공 해야 함)
    ]

    for i, pwd in enumerate(passwords_to_try, 1):
        print(f"\n[Attempt #{i}] 패스워드 '{pwd}' 입력 시도 중...")
        
        start_ts = time.time()
        result = authenticate_user(target_user, pwd, attacker_ip)
        duration = time.time() - start_ts
        
        if result:
            print(f"-> 결과: 성공 (소요시간: {duration:.4f}s)")
            break
        else:
            print(f"-> 결과: 실패 (소요시간: {duration:.4f}s)")
            
            # 실제 공격은 딜레이 없이 들어오지만, 방어 로직이 이를 막아내는 것을 확인
            
            if i == 5:
                print("-> 5회 연속 실패 후, 다음 시도 전 대기 필요 (지수 백오프 적용 중)...")
                time.sleep(5)  # 충분한 대기 시간 확보
            else:
                time.sleep(0.5) # 짧은 대기 시간으로 시도 간격 유지

    print("\n------------------------------------------------------------")
    print("[실습 결론]")
    print("1. Bcrypt 해시 검증은 의도적으로 CPU 자원을 소모하여 공격 속도를 늦춥니다.")
    print("2. 지수 백오프(Exponential Backoff)는 반복적인 실패 시 대기 시간을 기하급수적으로 늘려,")
    print("   공격자가 유효한 비밀번호를 추측하는 데 드는 비용을 막대하게 증가시킵니다.")

if __name__ == "__main__":
    main()