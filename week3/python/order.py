"""
--------------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : OOP 기반 AI 추천 주문 시스템 설계
# 작성일 : 2025-01-13
#
# 본 파일은 KDT 교육을 위한 Sample 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [실습 목표]
# 1. 클래스와 상속을 사용하여 메뉴 데이터 구조화
# 2. @property 데코레이터를 활용한 동적 데이터 계산 (총액, 평균)
# 3. 최근 주문 태그(Tag) 분석을 통한 단순 추천 알고리즘 구현
#
# [변경이력]
# 2026-01-13 : 초기 템플릿 작성 및 MenuItem 부모 클래스 정의
# 2026-01-13 : 중국 음식(ChineseFood) 자식 클래스 및 메뉴 데이터셋 구축
# 2026-01-13 : 주문 관리(OrderManager) 클래스 및 추천 로직(Intersection) 구현
--------------------------------------------------------------------------------
"""

from dataclasses import dataclass
import sys

# -----------------------------------------------------------------------------
# [Data Definition]
# -----------------------------------------------------------------------------
RAW_MENU_DATA = [
    ("짜장면", 7000, ["면", "식사"]),
    ("짬뽕", 8000, ["면", "식사"]),
    ("볶음밥", 8500, ["밥", "식사"]),
    ("탕수육", 18000, ["요리", "튀김"]),
    ("깐풍기", 25000, ["요리", "튀김"]),
    ("군만두", 6000, ["사이드", "튀김"]),
]

# -----------------------------------------------------------------------------
# [Helper Functions]
# -----------------------------------------------------------------------------

def format_currency(amount):
    """
    숫자형 데이터를 한국 원화 표기 형식의 문자열로 변환합니다.

    Args:
        amount (int or float): 변환할 금액

    Returns:
        str: 천 단위 콤마가 포함된 문자열 (예: "1,000원")
    """
    return f"{int(amount):,}원"


def print_section_title(title):
    """
    콘솔 출력 시 가독성을 높이기 위해 섹션 헤더를 포맷팅하여 출력합니다.

    Args:
        title (str): 섹션 제목

    Returns:
        None
    """
    print(f"\n" + "="*60)
    print(f" [System] {title}")
    print("="*60)


# -----------------------------------------------------------------------------
# [Business Logic Classes]
# -----------------------------------------------------------------------------

@dataclass
class MenuItem:
    """
    모든 메뉴 아이템의 공통 속성(이름, 가격)을 정의하는 기본 클래스입니다.
    
    Attributes:
        name (str): 메뉴 이름
        price (int): 메뉴 가격
    """
    name: str
    price: int

    def __str__(self):
        """객체의 문자열 표현을 '이름 (가격)' 형태로 반환합니다."""
        return f"{self.name} ({format_currency(self.price)})"


@dataclass
class ChineseFood(MenuItem):
    """
    MenuItem을 상속받아 음식의 특징(Tags) 정보를 추가로 관리하는 클래스입니다.

    Attributes:
        tags (list): 음식의 특징을 나타내는 문자열 리스트 (예: ["면", "매운맛"])
    """
    tags: list

    def get_info(self):
        """
        메뉴의 이름, 가격, 그리고 태그 정보를 포함한 상세 문자열을 반환합니다.

        Returns:
            str: 포맷팅된 메뉴 상세 정보
        """
        tag_str = ", ".join(self.tags)
        return f"[{self.name}] {format_currency(self.price)} | 특징: {tag_str}"


class OrderSystem:
    """
    사용자의 주문을 처리하고 통계 계산 및 메뉴 추천 기능을 제공하는 매니저 클래스입니다.
    """

    def __init__(self, menu_list):
        """
        OrderSystem 초기화 메서드

        Args:
            menu_list (list): 시스템에서 관리할 ChineseFood 객체들의 리스트
        """
        self.menu_list = menu_list
        self.order_history = []  # 주문 내역을 저장할 리스트 초기화

    def add_order(self, food_name):
        """
        사용자로부터 메뉴 이름을 입력받아 주문 내역에 추가합니다.

        Args:
            food_name (str): 주문할 음식의 이름

        Returns:
            None: 주문 성공 여부는 콘솔 출력으로 대체
        """
        # 전체 메뉴 리스트에서 이름이 일치하는 첫 번째 객체를 검색
        selected_food = next((food for food in self.menu_list if food.name == food_name), None)
        
        if selected_food:
            self.order_history.append(selected_food)
            print(f" >> 주문 완료: {selected_food.name}")
        else:
            print(f" >> 주문 실패: '{food_name}'은(는) 메뉴에 없습니다.")

    @property
    def total_price(self):
        """
        현재까지 저장된 주문 내역의 총 금액을 계산하여 반환합니다.
        
        Returns:
            int: 주문 총액
        """
        return sum(food.price for food in self.order_history)

    @property
    def average_price(self):
        """
        주문 내역의 평균 금액을 계산하여 반환합니다.
        
        Returns:
            float: 평균 주문 금액 (주문 내역이 없을 경우 0 반환)
        """
        if not self.order_history:
            return 0
        return self.total_price / len(self.order_history)

    def recommend_food(self):
        """
        사용자의 최근 주문 내역을 기반으로 유사한 스타일의 메뉴를 추천합니다.

        1. 가장 최근에 주문한 음식의 태그 리스트를 추출합니다.
        2. 메뉴판의 다른 음식들과 태그를 비교합니다.
        3. List Comprehension을 사용하여 겹치는 태그의 개수(유사도)를 계산합니다.
        4. 유사도가 높은 순서대로 정렬하여 상위 2개를 반환합니다.

        Returns:
            list: 추천된 메뉴 정보 문자열 리스트 (추천 불가 시 안내 메시지 리스트 반환)
        """
        if not self.order_history:
            return "주문 이력이 없어 추천할 수 없습니다."

        last_food = self.order_history[-1]
        target_tags = last_food.tags
        
        print(f"\n[AI 분석] 최근 드신 '{last_food.name}'의 특징 {target_tags}을(를) 분석 중...")

        recommendations = []
        for food in self.menu_list:
            # 방금 먹은 메뉴는 추천 대상에서 제외
            if food.name == last_food.name:
                continue
            
            # [유사도 계산]
            # target_tags와 food.tags 간의 공통 요소 개수를 산출
            common_tags = [t for t in target_tags if t in food.tags]
            match_count = len(common_tags)

            # 겹치는 태그가 하나라도 있는 경우 후보 리스트에 추가 (점수, 음식객체)
            if match_count > 0:
                recommendations.append((match_count, food))

        # 유사도 점수(match_count)를 기준으로 내림차순 정렬
        recommendations.sort(key=lambda x: x[0], reverse=True)

        if not recommendations:
            return ["비슷한 스타일의 메뉴가 없습니다."]
        
        # 상위 2개 항목을 사용자에게 보여줄 문자열로 변환하여 반환
        return [f"{item[1].name} (유사도 점수: {item[0]})" for item in recommendations[:2]]


# -----------------------------------------------------------------------------
# [Main Execution Flow]
# -----------------------------------------------------------------------------
if __name__ == "__main__":
    
    # 1. 데이터 초기화 및 시스템 인스턴스 생성
    #    (Raw Data 튜플을 ChineseFood 객체 리스트로 변환)
    menu_objects = [ChineseFood(name, price, tags) for name, price, tags in RAW_MENU_DATA]
    my_system = OrderSystem(menu_objects)

    print_section_title("중국집 AI 주문 시스템")

    # 2. 전체 메뉴 리스트 출력
    print(" [메뉴 목록]")
    for food in menu_objects:
        print(f" - {food.get_info()}")

    # 3. 주문 시나리오 실행
    print_section_title("사용자 주문 진행")
    my_system.add_order("짬뽕")
    my_system.add_order("탕수육")

    # 4. 주문 통계 확인
    print_section_title("주문 내역 정산")
    print(f" -> 현재 총 주문 금액 : {format_currency(my_system.total_price)}")
    print(f" -> 평균 주문 금액    : {format_currency(my_system.average_price)}")

    # 5. 추천 알고리즘 실행 및 결과 출력
    print_section_title("AI 메뉴 추천")
    recommended_items = my_system.recommend_food()
    
    print(" >> 추천 결과:")
    for item in recommended_items:
        print(f"    {item}")
        
    print("\n>>> 시스템 종료")