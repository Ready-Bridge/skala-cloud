# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : KDT 교육용 Python 실습 목적 코드
# 작성일 : 2025-01-12
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2025-01-12 : 직원 데이터 기초 분석 로직 구현 (부서/급여 필터링, 상위 급여 정렬 등 3건)
# 2025-01-12 : 부서별 평균 급여 계산(Grouping & Aggregation) 통계 함수 추가
# -----------------------------------------------------------------------------

# -----------------------------------------------------------------------------
# [Data Definition]
# -----------------------------------------------------------------------------
employees = [
    {"name": "Alice",   "department": "Engineering", "age": 30, "salary": 85000},
    {"name": "Bob",     "department": "Marketing",   "age": 25, "salary": 60000},
    {"name": "Charlie", "department": "Engineering", "age": 35, "salary": 95000},
    {"name": "David",   "department": "HR",          "age": 45, "salary": 70000},
    {"name": "Eve",     "department": "Engineering", "age": 28, "salary": 78000},
]

# -----------------------------------------------------------------------------
# [Helper Functions]
# - 메인 로직을 보조하는 단순 기능 함수들입니다.
# -----------------------------------------------------------------------------

def get_salary_value(emp):
    """
    정렬(sorting)을 위해 직원의 급여 값을 반환하는 헬퍼 함수입니다.
    
    Args:
        emp (dict): 직원 1명의 정보가 담긴 딕셔너리
        
    Returns:
        int: 해당 직원의 급여(salary)
    """
    return emp["salary"]

# -----------------------------------------------------------------------------
# [Business Logic Functions]
# - 실제 요구사항을 처리하는 핵심 함수들입니다.
# -----------------------------------------------------------------------------

def get_high_salary_engineers(data, target_dept="Engineering", min_salary=80000):
    """
    특정 부서 내에서 기준 급여 이상을 받는 직원의 이름을 리스트로 반환합니다.

    Args:
        data (list): 전체 직원 정보가 담긴 리스트
        target_dept (str): 찾고자 하는 부서명 (기본값: "Engineering")
        min_salary (int): 필터링 할 최소 급여 기준 (기본값: 80000)

    Returns:
        list: 조건에 부합하는 직원들의 이름(str)이 담긴 리스트
    """
    result_list = []

    for emp in data:
        # 부서가 일치하고, 급여가 기준 이상인지 확인
        if emp["department"] == target_dept and emp["salary"] >= min_salary:
            result_list.append(emp["name"])
            
    return result_list


def get_senior_employee_info(data, min_age=30):
    """
    기준 연령 이상인 직원의 이름과 부서 정보를 추출합니다.

    Args:
        data (list): 전체 직원 정보가 담긴 리스트
        min_age (int): 필터링 할 최소 나이 기준 (기본값: 30)

    Returns:
        list: (이름, 부서) 형태의 튜플(tuple)들이 담긴 리스트
    """
    result_list = []

    for emp in data:
        if emp["age"] >= min_age:
            # 이름과 부서를 튜플로 묶어서 저장
            info = (emp["name"], emp["department"])
            result_list.append(info)

    return result_list


def get_top_earners(data, top_n=3):
    """
    급여가 높은 순서대로 상위 N명의 이름과 급여를 반환합니다.
    원본 데이터의 순서를 변경하지 않기 위해 sorted()를 사용합니다.

    Args:
        data (list): 전체 직원 정보가 담긴 리스트
        top_n (int): 반환할 상위 인원 수 (기본값: 3)

    Returns:
        list: (이름, 급여) 형태의 튜플(tuple)들이 담긴 리스트
    """
    # 1. 급여 기준으로 내림차순 정렬 (원본 보존)
    # key=get_salary_value : 정렬할 때 get_salary_value 함수를 통해 급여값을 비교함
    sorted_employees = sorted(
        data, 
        key=get_salary_value, 
        reverse=True
    )
    
    result_list = []
    
    # 2. 정렬된 리스트에서 상위 N명만 추출
    for emp in sorted_employees[:top_n]:
        info = (emp["name"], emp["salary"])
        result_list.append(info)
    
    return result_list


def get_average_salary_by_department(data):
    """
    모든 부서의 평균 급여를 계산하여 딕셔너리로 반환합니다.
    
    Logic:
        1. 데이터를 순회하며 부서별로 급여를 리스트에 모읍니다. (Grouping)
        2. 각 부서별 급여 리스트의 합계와 개수를 통해 평균을 구합니다. (Aggregation)

    Args:
        data (list): 전체 직원 정보가 담긴 리스트

    Returns:
        dict: { "부서명": 평균급여(int), ... } 형태의 딕셔너리
    """
    
    # [Step 1] 부서별로 급여 모으기 (Grouping)
    # 예: {"Engineering": [85000, 95000, ...], "HR": [70000]}
    dept_salary_map = {}

    for emp in data:
        dept = emp["department"]
        salary = emp["salary"]

        # 딕셔너리에 해당 부서 키가 없으면 빈 리스트 생성
        if dept not in dept_salary_map:
            dept_salary_map[dept] = []
        
        # 해당 부서 리스트에 급여 추가
        dept_salary_map[dept].append(salary)
    
    # [Step 2] 각 부서별 평균 계산하기 (Aggregation)
    average_results = {}

    # 딕셔너리의 키(부서명)를 하나씩 꺼내서 반복
    for dept in dept_salary_map:
        salaries = dept_salary_map[dept] # 해당 부서의 급여 리스트
        
        total_salary = sum(salaries)     # 급여 합계
        count = len(salaries)            # 직원 수
        
        # 평균 계산 (소수점 버림을 위해 int로 변환)
        average = int(total_salary / count)
        
        average_results[dept] = average

    return average_results


# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    print("--- [직원 데이터 분석 결과] ---\n")

    # 1. Engineering 부서 & 고연봉자 조회
    engineers = get_high_salary_engineers(employees)
    print(f"문제 1. 고연봉 엔지니어 명단: {engineers}")

    # 2. 30세 이상 직원 조회
    seniors = get_senior_employee_info(employees)
    print(f"문제 2. 시니어 직원(30세 이상) 정보: {seniors}")

    # 3. 급여 상위 3인 조회
    top_earners = get_top_earners(employees)
    print(f"문제 3. 급여 상위 3명: {top_earners}")

    # 4. 부서별 평균 급여 조회
    avg_salaries = get_average_salary_by_department(employees)
    print(f"문제 4. 부서별 평균 급여: {avg_salaries}")