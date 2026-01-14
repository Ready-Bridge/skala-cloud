# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : 대용량 리뷰 데이터 병렬 마스킹 및 정규화(Normalization) 처리
# 작성일 : 2026-01-13
#
# 본 파일은 KDT 교육을 위한 실습 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-13 : 초기 버전 생성 (JSON/CSV 로더, 마스킹 로직, 직렬/병렬 처리 구현)
# 2026-01-13 : JSONL(Line-by-Line) 포맷 지원 및 데이터 컬럼명(review_text) 수정
# 2026-01-13 : 공백 포함 전화번호 정규식 패턴 확장
# 2026-01-13 : Type Hinting 적용 및 Path Traversal 보안 로직 추가
# 2026-01-13 : Chunking 전략 개선 및 변경 건수(Count) 기반 검증 로직으로 변경
# 2026-01-13 : 성능 비교 문구 구체화 및 마스킹 결과 예시 출력 추가
# -----------------------------------------------------------------------------

import re
import json
import csv
import time
import os
import multiprocessing
from typing import List, Dict, Tuple, Optional, Pattern

# -----------------------------------------------------------------------------
# [Configuration & Constants]
# -----------------------------------------------------------------------------

# 데이터 파일이 위치해야 하는 기본 디렉토리
BASE_DATA_DIR = os.path.abspath("data_masking_parallel/data")

# 성능: 하나의 프로세스가 한 번에 처리할 최대 청크 크기 제한
# 너무 큰 청크는 실패 시 재시도 비용이 크고, 로드 밸런싱 효율이 떨어짐
MAX_CHUNK_SIZE = 5000

# 마스킹 처리를 위한 정규표현식 패턴 컴파일
EMAIL_PATTERN: Pattern = re.compile(r'[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}')
PHONE_PATTERN: Pattern = re.compile(r'\d{2,3}[\s-]\d{3,4}[\s-]\d{4}')

# 금칙어 매핑
BANNED_WORDS: Dict[str, str] = {
    "비속어1": "나쁜말",
    "비속어2": "부적절한표현",
    "비하_표현": "부적절한언어",
    "비하표현": "부적절한언어",
    "광고": "홍보성문구"
}

# -----------------------------------------------------------------------------
# [Helper Functions]
# -----------------------------------------------------------------------------

def _get_safe_path(file_name: str) -> str:
    """
    Path Traversal 공격 방지를 위해 파일 경로를 검증하고 절대 경로를 반환합니다.
    
    Args:
        file_name (str): 입력받은 파일명
        
    Returns:
        str: 검증된 절대 경로
        
    Raises:
        ValueError: 허용되지 않는 경로일 경우
    """
    # 파일명에서 디렉토리 경로 제거 (예: ../etc/passwd -> passwd)
    safe_name = os.path.basename(file_name)
    target_path = os.path.abspath(os.path.join(BASE_DATA_DIR, safe_name))
    
    # 최종 경로가 BASE_DATA_DIR로 시작하는지 확인
    if not target_path.startswith(BASE_DATA_DIR):
        raise ValueError(f"Security Alert: 허용되지 않는 경로 접근 시도 - {file_name}")
        
    return target_path


def load_data(file_name: str) -> List[str]:
    """
    파일 확장자에 따라 JSONL 또는 CSV 파일을 로드합니다.
    
    Args:
        file_name (str): data 폴더 내의 파일명
        
    Returns:
        List[str]: 리뷰 텍스트 리스트
    """
    data_list: List[str] = []
    
    try:
        file_path = _get_safe_path(file_name)
        
        if not os.path.exists(file_path):
            print(f"[Error] 파일을 찾을 수 없습니다: {file_path}")
            return []

        ext = os.path.splitext(file_path)[-1].lower()

        if ext in ['.jsonl', '.json']:
            with open(file_path, 'r', encoding='utf-8') as f:
                for line in f:
                    if not line.strip(): continue
                    try:
                        item = json.loads(line)
                        text = item.get("review_text", "")
                        data_list.append(text)
                    except json.JSONDecodeError:
                        continue
                        
        elif ext == '.csv':
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                data_list = [row.get("review_text", "") for row in reader]
                
    except Exception as e:
        print(f"[Error] 데이터 로딩 중 오류 발생: {e}")

    return data_list


def mask_and_normalize(text: str) -> Tuple[str, int]:
    """
    단일 텍스트에 대해 마스킹 및 정규화를 수행하고, 변경 여부를 반환합니다.

    Args:
        text (str): 원본 텍스트

    Returns:
        Tuple[str, int]: (처리된 텍스트, 변경 발생 횟수 1 or 0)
    """
    if not isinstance(text, str):
        return str(text), 0

    original_text = text

    # 1. Regex 마스킹
    text = EMAIL_PATTERN.sub("****", text)
    text = PHONE_PATTERN.sub("***-****-****", text)

    # 2. 금칙어 순화
    for bad_word, replacement in BANNED_WORDS.items():
        if bad_word in text:
            text = text.replace(bad_word, replacement)

    # 변경 여부 확인 (내용이 달라졌으면 1, 아니면 0)
    is_changed = 1 if text != original_text else 0

    return text, is_changed

# -----------------------------------------------------------------------------
# [Business Logic Functions]
# -----------------------------------------------------------------------------

def process_serial(data_list: List[str]) -> Tuple[List[str], int]:
    """
    직렬 처리 로직입니다.
    
    Returns:
        Tuple[List[str], int]: (결과 리스트, 총 변경 건수)
    """
    results = []
    total_changes = 0
    
    for text in data_list:
        processed_text, change_count = mask_and_normalize(text)
        results.append(processed_text)
        total_changes += change_count
        
    return results, total_changes


def process_chunk(chunk: List[str]) -> Tuple[List[str], int]:
    """
    [Worker] 할당된 청크 데이터를 처리하고 결과와 변경 건수를 집계합니다.
    """
    chunk_results = []
    chunk_changes = 0
    
    for text in chunk:
        processed_text, change_count = mask_and_normalize(text)
        chunk_results.append(processed_text)
        chunk_changes += change_count
        
    return chunk_results, chunk_changes


def process_parallel(data_list: List[str], num_processes: Optional[int] = None) -> Tuple[List[str], int]:
    """
    병렬 처리 로직입니다.
    데이터를 적절한 크기의 청크로 나누어 처리합니다.
    """
    if not data_list:
        return [], 0

    if num_processes is None:
        num_processes = multiprocessing.cpu_count()

    total_len = len(data_list)
    
    # Chunking 전략:
    # 1. 코어 수보다 4배수 정도로 잘게 나누어 로드 밸런싱 유도
    # 2. 단, MAX_CHUNK_SIZE를 넘지 않도록 제한
    calculated_size = total_len // (num_processes * 4)
    if calculated_size < 1:
        calculated_size = 1
        
    chunk_size = min(calculated_size, MAX_CHUNK_SIZE)
    
    # 데이터 슬라이싱
    chunks = [data_list[i:i + chunk_size] for i in range(0, total_len, chunk_size)]

    # 병렬 실행
    with multiprocessing.Pool(processes=num_processes) as pool:
        # 각 워커는 (결과리스트, 변경건수) 튜플을 반환함
        chunk_outputs = pool.map(process_chunk, chunks)

    # 결과 취합 (Aggregation)
    final_result_list = []
    total_change_count = 0
    
    for c_res, c_cnt in chunk_outputs:
        final_result_list.extend(c_res)
        total_change_count += c_cnt

    return final_result_list, total_change_count


def run_batch_analysis(file_name: str, description: str) -> None:
    """
    배치 실행 및 검증 함수
    """
    print(f"========== [Scenario: {description}] ==========")
    print(f"Target File: {file_name}")
    
    # 1. 데이터 로딩
    raw_data = load_data(file_name)
    if not raw_data:
        print("[Skip] 데이터를 로드하지 못해 테스트를 중단합니다.\n")
        return

    print(f"[Info] 데이터 로드 완료: {len(raw_data):,}건")
    
    # 2. 직렬 처리
    start_time = time.time()
    serial_results, serial_changes = process_serial(raw_data)
    serial_duration = time.time() - start_time
    print(f"[Result] 직렬 처리: {serial_duration:.4f}초 | 변경된 건수: {serial_changes:,}건")

    # 3. 병렬 처리
    cpu_cores = multiprocessing.cpu_count()
    start_time = time.time()
    _, parallel_changes = process_parallel(raw_data, num_processes=cpu_cores)
    parallel_duration = time.time() - start_time
    print(f"[Result] 병렬 처리: {parallel_duration:.4f}초 | 변경된 건수: {parallel_changes:,}건 (Core: {cpu_cores})")

    # 4. 검증 및 결과 분석
    is_valid = (serial_changes == parallel_changes)
    print(f"[Check] 정합성 검증(변경 건수 일치): {is_valid}")

    if serial_duration > 0 and parallel_duration > 0:
        if serial_duration > parallel_duration:
            ratio = serial_duration / parallel_duration
            print(f"[Analysis] 성능 차이: 병렬 처리가 직렬 처리보다 약 {ratio:.2f}배 빠릅니다.")
        else:
            ratio = parallel_duration / serial_duration
            print(f"[Analysis] 성능 차이: 직렬 처리가 병렬 처리보다 약 {ratio:.2f}배 빠릅니다.")
    
    # 5. 마스킹 예시 출력 (첫 번째 데이터 기준)
    if serial_results:
        print(f"\n[Example] 변환 전: {raw_data[0]}")
        print(f"[Example] 변환 후: {serial_results[0]}")
    
    print("=" * 50 + "\n")

# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------

if __name__ == "__main__":
    print("--- [데이터 정제 배치 프로세스 시작] ---\n")

    # 1. JSONL 데이터 (100k) 처리
    run_batch_analysis("reviews_100k.jsonl", "100K JSONL Review Data")

    # 2. CSV 데이터 (500k) 처리
    run_batch_analysis("reviews_500k.csv", "500K CSV Review Data")