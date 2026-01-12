"""
--------------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : .env 환경변수 로드 및 logging 모듈 활용 실습 (콘솔/파일 출력)
# 작성일 : 2026-01-12
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-12 : 초기 템플릿 작성
# 2026-01-12 : python-dotenv를 이용한 환경변수 로드 기능 구현
# 2026-01-12 : logging 모듈 설정 및 예외 처리(ZeroDivisionError) 로직 추가
--------------------------------------------------------------------------------
"""

import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

# ==============================================================================
# SECTION 1: HELPER FUNCTIONS (설정 및 유틸리티)
# ==============================================================================

def init_environment():
    """
    .env 파일을 로드하고 환경 변수 유효성을 검증합니다.
    """
    load_dotenv()
    # 필수 변수 확인 로직
    if not os.getenv("APP_NAME"):
        print("[CRITICAL] APP_NAME is not defined in .env")
        sys.exit(1)

def get_logger(name):
    """
    로깅 설정을 초기화하고 로거 인스턴스를 반환합니다.
    """
    # 로거 생성
    logger = logging.getLogger(name)
    
    # .env에서 로그 레벨 가져오기 (Default: INFO)
    env_log_level = os.getenv("LOG_LEVEL", "INFO").upper()
    level = getattr(logging, env_log_level, logging.INFO)
    logger.setLevel(level)

    # 핸들러 중복 추가 방지
    if logger.handlers:
        return logger

    # ---------------------------------------------------------
    # 1. 콘솔 핸들러 (Console) - 파일과 동일하게 상세하게 변경
    # ---------------------------------------------------------
    console_handler = logging.StreamHandler()
    # 콘솔에서도 DEBUG 레벨까지 모두 출력되도록 설정
    console_handler.setLevel(logging.DEBUG) 
    
    console_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
    )
    console_handler.setFormatter(console_format)

    # 2. 파일 핸들러 (File) - 현재 경로의 app.log에 통합 저장
    file_handler = TimedRotatingFileHandler(
        filename="app.log",
        when="midnight",
        interval=1,
        backupCount=7,
        encoding="utf-8"
    )
    file_handler.setLevel(logging.DEBUG) # 파일에는 모든 상세 로그 기록
    file_format = logging.Formatter(
        "%(asctime)s | %(levelname)s | %(filename)s:%(lineno)d | %(message)s"
    )
    file_handler.setFormatter(file_format)

    # 핸들러 등록
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# ==============================================================================
# SECTION 2: BUSINESS LOGIC (핵심 비즈니스 로직)
# ==============================================================================

def run_business_process(logger):
    """
    실제 어플리케이션의 동작 시나리오를 수행합니다.
    """
    app_name = os.getenv("APP_NAME")

    # 1. 앱 실행 로그
    logger.info("앱 실행 시작")

    # 2. 환경 변수 로딩 확인 로그 (DEBUG 레벨 - 이제 콘솔에서도 보임)
    logger.debug(f"환경 변수 로딩 완료 (APP_NAME: {app_name})")

    # 3. 비즈니스 로직 수행 중 예외 처리 시나리오
    logger.info("비즈니스 로직 처리 중...")
    
    try:
        # 강제 예외 발생 (ZeroDivisionError)
        _ = 1 / 0
    except ZeroDivisionError:
        # exc_info=True: Traceback 정보를 로그 파일과 콘솔에 남김
        logger.error("예외 발생 예시: 0으로 나눌 수 없습니다.", exc_info=True)
    
    logger.info("앱 실행 종료")

# ==============================================================================
# SECTION 3: MAIN EXECUTION (실행 진입점)
# ==============================================================================

if __name__ == "__main__":
    # 1. 환경 설정 초기화
    init_environment()

    # 2. 로거 생성 (App Name 기반)
    current_app_name = os.getenv("APP_NAME", "UnknownApp")
    app_logger = get_logger(current_app_name)

    # 3. 비즈니스 로직 실행
    run_business_process(app_logger)