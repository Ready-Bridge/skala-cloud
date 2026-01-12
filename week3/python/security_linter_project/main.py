"""
--------------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : AST(Abstract Syntax Tree)를 활용한 Python 코드 정적 보안 분석기 구현
# 작성일 : 2026-01-12
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-12 : 초기 템플릿 작성 및 환경변수 로드 구현
# 2026-01-12 : Logging 설정 (콘솔 상세 출력 및 파일 핸들러 통합)
# 2026-01-12 : AST NodeVisitor를 상속받은 보안 취약점 탐지 로직(Business Logic) 구현
# 2026-01-12 : 리포트 출력 형식 개선 (파일명 명시 및 상세 정보 구조화)
--------------------------------------------------------------------------------
"""

import ast
import os
import sys
import logging
from logging.handlers import TimedRotatingFileHandler
from dotenv import load_dotenv

# ==============================================================================
# HELPER FUNCTIONS (설정 및 유틸리티)
# ==============================================================================

def init_environment():
    """
    .env 파일을 로드하고 필수 환경 변수의 유효성을 검증합니다.

    Returns:
        None

    Raises:
        SystemExit: 필수 환경 변수(APP_NAME)가 설정되지 않은 경우 프로그램 종료
    """
    load_dotenv()
    # 필수 변수 확인 로직
    if not os.getenv("APP_NAME"):
        print("[CRITICAL] APP_NAME is not defined in .env")
        sys.exit(1)

def get_logger(name):
    """
    애플리케이션 전역 로깅 설정을 초기화하고 로거 인스턴스를 생성하여 반환합니다.
    콘솔(StreamHandler) 및 파일(TimedRotatingFileHandler) 핸들러를 포함합니다.

    Args:
        name (str): 생성할 로거의 이름

    Returns:
        logging.Logger: 설정이 완료된 로거 인스턴스
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
    # 1. 콘솔 핸들러 (Console)
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
# BUSINESS LOGIC (AST 보안 분석기)
# ==============================================================================

# ast.NodeVisitor를 상속받으면 파이썬이 만든 코드 분석 나무(Tree)를 구석구석 돌아다닐 수 있음
class SecurityNodeVisitor(ast.NodeVisitor):
    """
    Python 코드를 순회(Traverse)하며 보안 위협이 있는 함수 호출을 탐지하는 클래스입니다.
    """
    # 생성자
    def __init__(self, logger, filename):
        """
        SecurityNodeVisitor 인스턴스를 초기화합니다.

        Args:
            logger (logging.Logger): 보안 취약점 탐지 로그를 기록할 로거 객체
            filename (str): 분석 대상 소스 코드 파일의 이름
        """
        # 취약점 발견 시 보고할 logger를 연결
        self.logger = logger
        self.filename = filename
        # 총 몇 개의 위험 요소가 발견되었는지 세어줄 카운터
        self.issues_found = 0
        
        # 1. 단독으로 사용되는 위험한 함수 이름 정의 (예: eval(), exec())
        self.dangerous_calls = {
            'eval': '임의 코드 실행 가능성 높음',
            'exec': '임의 코드 실행 가능성 높음',
        }
        
        # 2. 특정 모듈 안에 소속된 위험한 메서드 정의 (예: os.system())
        # 'os' 모듈의 'system'이나 'popen'은 운영체제 명령어를 조작할 수 있어 위험
        self.dangerous_modules = {
            'os': ['system', 'popen'],        # 시스템 제어 관련
            'pickle': ['load', 'loads'],      # 외부 데이터 변환(역직렬화) 시 악성코드 실행 위험
            'subprocess': ['call', 'run']     # 외부 프로그램 실행 관련
        }

    def visit_Call(self, node):
        """
        AST 순회 중 함수 호출(Call) 노드를 방문할 때 실행되는 메서드입니다.
        호출된 함수가 위험 목록(dangerous_calls, dangerous_modules)에 포함되는지 검사합니다.

        Args:
            node (ast.Call): 현재 방문 중인 함수 호출 노드
        """
        # [상황 1] 함수를 이름으로 직접 부르는 경우 (예: eval("1+1"))
        # node.func가 '이름(ast.Name)' 형태인지 확인합니다.
        if isinstance(node.func, ast.Name):
            func_name = node.func.id  # 실제 함수의 이름(id)을 가져옵니다.
            
            # 그 이름이 우리가 미리 정한 '위험한 함수' 목록에 들어있는지 확인합니다.
            if func_name in self.dangerous_calls:
                # 맞다면 로그를 남깁니다 (줄 번호, 함수명, 위험 이유 전달)
                self.log_vulnerability(node.lineno, func_name, self.dangerous_calls[func_name])

        # [상황 2] 점(.)을 찍어서 호출하는 경우 (예: os.system("명령어"))
        # node.func가 '속성(ast.Attribute)' 형태(객체.속성)인지 확인합니다.
        elif isinstance(node.func, ast.Attribute):
            # 점 앞부분(node.func.value)이 단순한 이름(ast.Name)인지 확인합니다 (예: 'os')
            if isinstance(node.func.value, ast.Name):
                module_name = node.func.value.id  # 점 앞의 이름 (예: 'os')
                method_name = node.func.attr      # 점 뒤의 이름 (예: 'system')
                
                # 먼저 'os'나 'pickle' 같은 위험 모듈 리스트에 있는지 확인합니다.
                if module_name in self.dangerous_modules:
                    # 해당 모듈 안에 정의된 구체적인 위험 함수명과 일치하는지 확인합니다.
                    if method_name in self.dangerous_modules[module_name]:
                        msg = f"{module_name}.{method_name} 사용 감지 (시스템 명령어/역직렬화 위험)"
                        self.log_vulnerability(node.lineno, f"{module_name}.{method_name}", msg)

        # 내 할 일을 다 했으니, 이 함수 호출 안에 또 다른 함수 호출이 숨어있을 수 있으므로
        # 자식 노드들을 계속해서 탐색하라고 시킴
        self.generic_visit(node)

    def log_vulnerability(self, lineno, func_signature, reason):
        """
        탐지된 보안 취약점 정보를 로깅하고 카운트를 증가시킵니다.
        이모지를 제외한 텍스트 기반의 구조화된 리포트를 경고(Warning) 레벨로 출력합니다.

        Args:
            lineno (int): 취약점이 발견된 소스 코드 라인 번호
            func_signature (str): 문제가 되는 함수 또는 메서드의 시그니처
            reason (str): 해당 호출이 보안 위협으로 간주되는 상세 사유
        """
        self.issues_found += 1
        
        # [취약점 리포트 생성] 가독성을 위해 여러 줄로 출력
        report_msg = (
            f"\n[Security Violation Report]\n"
            f" - File   : {self.filename}\n"
            f" - Line   : {lineno}\n"
            f" - Call   : {func_signature}\n"
            f" - Reason : {reason}\n"
        )
        # logger.warning 레벨을 사용하여 주의 깊게 봐야 함을 알립니다.
        self.logger.warning(report_msg)

def run_security_scan(logger):
    """
    보안 검사 시나리오를 실행합니다.
    가상의 소스 코드를 대상으로 AST 파싱 및 SecurityNodeVisitor를 이용한 정적 분석을 수행합니다.

    Args:
        logger (logging.Logger): 실행 로그를 기록할 로거 인스턴스

    Returns:
        None
    """
    app_name = os.getenv("APP_NAME")
    logger.info("보안 검사 프로세스 시작")
    logger.debug(f"환경 변수 로딩 완료 (APP_NAME: {app_name})")

    # [테스트용 취약한 코드 샘플]
    target_filename = "virtual_script.py"
    source_code = """
import os
import pickle

def process_data(data):
    # 1. 위험한 eval 사용
    result = eval(data) 
    
    # 2. 안전한 print 사용
    print("Processing...")

    # 3. 위험한 os.system 사용
    os.system("rm -rf /")

    # 4. 위험한 pickle 로드
    with open('data.pkl', 'rb') as f:
        obj = pickle.load(f)

    return result
"""
    logger.info(f"분석 대상 파일 로드: {target_filename}")

    try:
        # 1. AST 파싱 (문자열인 소스코드를 파이썬이 이해하는 Tree 구조로 변환)
        tree = ast.parse(source_code)
        
        # 2. Visitor(Tree 탐색) 생성 및 분석 실행
        # [수정] Visitor 생성 시 target_filename 전달
        visitor = SecurityNodeVisitor(logger, target_filename)
        visitor.visit(tree)
        
        # 3. 결과 요약 출력
        if visitor.issues_found == 0:
            logger.info("검사 완료: 발견된 취약점 없음 (Clean)")
        else:
            logger.error(f"검사 완료: 총 {visitor.issues_found}건의 보안 취약점 발견됨")

    except SyntaxError:
        logger.error(f"분석 실패: {target_filename}에 문법 오류가 있습니다.", exc_info=True)
    except Exception:
        logger.error("분석 중 치명적인 오류 발생", exc_info=True)

    logger.info("보안 검사 프로세스 종료")

# ==============================================================================
# MAIN EXECUTION (실행 진입점)
# ==============================================================================

if __name__ == "__main__":
    # 1. 환경 설정 초기화
    init_environment()

    # 2. 로거 생성 (App Name 기반)
    current_app_name = os.getenv("APP_NAME", "UnknownApp")
    app_logger = get_logger(current_app_name)

    # 3. 비즈니스 로직(보안 검사) 실행
    run_security_scan(app_logger)