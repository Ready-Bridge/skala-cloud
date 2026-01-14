# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : 구조적 로깅 및 컨텍스트 추적
# 작성일 : 2026-01-13
#
# 본 파일은 KDT 교육을 위한 실습 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-13 : 초기 버전 생성 (CSV 로더, CPU 시뮬레이션, 멀티프로세스 로깅 구현)
# 2026-01-13 : Race Condition 방지를 위한 QueueListener 패턴 적용
# 2026-01-13 : JSON 포맷팅 표준화 및 Context 데이터 구조 설계
# 2026-01-13 : multiprocessing.Pool과의 호환성을 위해 Manager().Queue()로 변경
# -----------------------------------------------------------------------------

import csv
import json
import time
import os
import datetime
import multiprocessing
import math
import threading
from typing import Dict, Any, List

# -----------------------------------------------------------------------------
# [Configuration & Constants]
# -----------------------------------------------------------------------------

# 데이터 경로 설정 (OS 독립적 경로 생성)
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
INPUT_FILE = os.path.join(BASE_DIR, "data", "input_tasks.csv")
LOG_FILE = os.path.join(BASE_DIR, "data", "application_logs.json")

# CPU 작업 강도 시뮬레이션 상수
CPU_LOAD_FACTOR = 10000

# -----------------------------------------------------------------------------
# [Logging Infrastructure]
# - 멀티프로세스 환경에서 안전하게 로그를 남기기 위한 인프라입니다.
# -----------------------------------------------------------------------------

def log_listener(queue: multiprocessing.Queue, log_file_path: str):
    """
    [Consumer Process]
    여러 워커 프로세스에서 보낸 로그 메시지를 큐에서 꺼내 파일에 순차적으로 기록합니다.
    이 방식을 통해 파일 쓰기 시점의 Race Condition을 방지합니다.

    Args:
        queue (multiprocessing.Queue): 로그 메시지가 담긴 큐
        log_file_path (str): 로그를 기록할 파일 경로
    """
    # 파일 모드 'a'(append)로 열어 계속 추가
    with open(log_file_path, 'a', encoding='utf-8') as f:
        while True:
            try:
                # 큐에서 메시지 수신 (Blocking)
                record = queue.get()
                
                # 종료 신호(None)를 받으면 루프 종료
                if record is None:
                    break
                
                # JSON 객체를 문자열로 변환하여 기록
                f.write(json.dumps(record, ensure_ascii=False) + "\n")
                f.flush()  # 버퍼 강제 비우기 (실시간 확인을 위해)
                
            except Exception as e:
                print(f"[System Error] 로그 기록 중 오류 발생: {e}")

def create_log_record(level: str, task_info: Dict[str, Any], stage: str, message: str) -> Dict[str, Any]:
    """
    로그 포맷을 표준화하여 딕셔너리로 반환합니다.

    Args:
        level (str): 로그 레벨 (INFO, ERROR, WARN)
        task_info (dict): CSV에서 읽어온 태스크 정보
        stage (str): 작업 단계 (START, PROCESSING, END)
        message (str): 사람이 읽을 수 있는 메시지

    Returns:
        dict: JSON 변환을 위한 표준 로그 구조
    """
    now_utc = datetime.datetime.now(datetime.timezone.utc).isoformat()
    
    return {
        "timestamp": now_utc,
        "level": level,
        "batch_id": task_info.get("batch_id"),
        "task_id": task_info.get("task_id"),
        "process_id": os.getpid(),
        "thread_id": threading.current_thread().name,
        "stage": stage,
        "message": message,
        "context": {
            "job_type": task_info.get("job_type"),
            "input_size_mb": int(task_info.get("input_size_mb", 0)),
            "priority": task_info.get("priority")
        }
    }

# -----------------------------------------------------------------------------
# [Business Logic Functions]
# - 실제 데이터 처리 및 CPU 바운드 작업을 시뮬레이션합니다.
# -----------------------------------------------------------------------------

def process_task_worker(task: Dict[str, Any], log_queue: multiprocessing.Queue):
    """
    [Worker Process]
    할당된 태스크를 처리하고 로그를 큐로 전송합니다.

    Args:
        task (dict): 처리할 태스크 정보
        log_queue (multiprocessing.Queue): 메인 프로세스의 리스너로 연결된 큐
    """
    try:
        # 1. 작업 시작 로그
        start_log = create_log_record("INFO", task, "START", "Task processing started")
        log_queue.put(start_log)

        # 2. CPU 바운드 작업 시뮬레이션 (데이터 크기에 비례한 연산)
        input_size = int(task.get("input_size_mb", 0))
        target_count = input_size * CPU_LOAD_FACTOR
        
        # 단순 연산으로 CPU 점유
        result = 0
        for i in range(target_count):
            result += math.sqrt(i + 1)

        # 3. 작업 완료 로그
        end_log = create_log_record("INFO", task, "COMPLETE", "Task processing finished successfully")
        log_queue.put(end_log)

    except Exception as e:
        # 에러 발생 시 로그
        error_log = create_log_record("ERROR", task, "FAIL", f"Processing failed: {str(e)}")
        log_queue.put(error_log)


def load_tasks(file_path: str) -> List[Dict[str, Any]]:
    """
    CSV 파일을 읽어 태스크 리스트를 반환합니다.

    Args:
        file_path (str): CSV 파일 경로

    Returns:
        list: 태스크 딕셔너리 리스트
    """
    tasks = []
    if not os.path.exists(file_path):
        print(f"[Error] 입력 파일을 찾을 수 없습니다: {file_path}")
        return tasks

    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            tasks.append(row)
    return tasks

# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------

def main():
    print("--- [대용량 로그 파이프라인 시작] ---")
    
    # 1. 데이터 로드
    tasks = load_tasks(INPUT_FILE)
    if not tasks:
        return
    print(f"[Info] 총 {len(tasks)}개의 태스크가 로드되었습니다.")

    # 2. 멀티프로세싱 리소스 설정
    # Manager().Queue() 사용 이유: 일반 Queue는 Pool의 워커로 전달(Pickle)될 수 없으나, 
    # Manager 프록시 객체는 프로세스 풀 간에 안전하게 공유 및 전달이 가능함 (RuntimeError 방지)
    manager = multiprocessing.Manager()
    log_queue = manager.Queue()

    # 3. 로그 리스너 프로세스 시작 (별도 프로세스에서 파일 쓰기 전담)
    listener_process = multiprocessing.Process(
        target=log_listener, 
        args=(log_queue, LOG_FILE)
    )
    listener_process.start()
    
    # 4. 워커 프로세스 풀 생성 및 작업 할당
    # CPU 코어 수만큼 프로세스 생성
    num_cores = multiprocessing.cpu_count()
    print(f"[Info] {num_cores}개의 워커 프로세스로 작업을 시작합니다...")
    
    # 
    
    start_time = time.time()
    
    with multiprocessing.Pool(processes=num_cores) as pool:
        # map 대신 starmap_async나 apply_async를 써야 인자 전달이 용이하지만,
        # pool.map은 단일 인자만 받으므로 튜플을 가져온 뒤, 그 안의 내용물을 풀어서 함수에 꽂아주는 starmap을 사용.
        
        # 각 태스크에 큐를 인자로 전달하기 위해 준비
        pool.starmap(process_task_worker, [(task, log_queue) for task in tasks])

    duration = time.time() - start_time
    print(f"[Info] 모든 작업 처리 완료 (소요시간: {duration:.2f}초)")

    # 5. 리소스 정리
    # 리스너에게 종료 신호 전송
    log_queue.put(None)
    listener_process.join() # 현재 프로세스가 끝날 때까지 Main 프로세스 대기
    
    print(f"[Info] 로그 파일 생성 완료: {LOG_FILE}")
    print("--- [파이프라인 종료] ---")

if __name__ == "__main__":
    # Windows 환경에서의 프로세스 무한 복제를 막음
    multiprocessing.freeze_support()
    main()