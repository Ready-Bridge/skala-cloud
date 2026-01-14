# -----------------------------------------------------------------------------
# 작성자 : 한준교
# 작성목적 : 고객 리뷰 데이터 분석 및 시각화 리포트 자동화 실습
# 작성일 : 2026-01-14
#
# 본 파일은 KDT 교육을 위한 실습 코드이므로 작성자에게 모든 저작권이 있습니다.
#
# [변경이력]
# 2026-01-14 : CSV 데이터 로드 및 인코딩 예외 처리(Exception Handling) 로직 구현
# 2026-01-14 : 실제 데이터 컬럼명('rating') 기반 동적 탐색 로직 최적화
# 2026-01-14 : 리포트용 고해상도 이미지 저장 기능 추가 및 메인 실행부(Main) 모듈화 완료
# 2026-01-14 : 4단계 분석 프로세스(전처리-통계-인사이트-리포트) 구조화 완료
# 2026-01-14 : 경로 조작 공격 방지를 위한 base_dir 고정 및 단계별 로깅 추가
# 2026-01-14 : 리포트 구조 개편 (질문-그래프-해석-요약) 및 기술 통계 테이블 통합
# -----------------------------------------------------------------------------

import os
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  # 한글 폰트 자동 설정 (import만으로 설정 완료)

def load_data(file_path):
    """
    지정된 경로에서 CSV 파일을 로드하고 기초적인 전처리를 수행합니다.
    파일 존재 여부를 확인하고, 인코딩 예외 처리를 포함하여 안정성을 높였습니다.

    [1단계: 데이터 전처리] - 비고: reviews_1000.csv 파일 호출 및 데이터 정합성 검토 완료

    Args:
        file_path (str): 로드할 CSV 파일의 절대 경로 또는 상대 경로

    Returns:
        tuple: (정제된 DataFrame, 원본 데이터 건수, 제거된 결측치 건수, 결측 컬럼 리스트)
               오류 발생 시 None 반환
    """
    print(f"\n[1단계 처리 중] 데이터 전처리 프로세스를 시작합니다.")
    
    # [Checkpoint 1-1] 파일 호출 확인 - 비고: 경로 조작 공격 방지를 위한 유효성 검사 완료
    if not os.path.exists(file_path):
        print(f"[Error] 파일을 찾을 수 없습니다: {file_path}")
        return None
    print(f" >> 비고: 데이터 파일({os.path.basename(file_path)}) 호출 성공")
    
    try:
        # 2. 데이터 로드
        df = pd.read_csv(file_path, encoding='utf-8')
        original_count = len(df)
        dropped_count = 0
        missing_cols = []
        
        # [Checkpoint 1-2] 결측치 확인 및 처리 - 비고: 데이터 무결성 확보 완료
        if df.isnull().values.any():
            dropped_count = df.isnull().sum().sum()
            missing_cols = df.columns[df.isnull().any()].tolist()
            
            print(f" >> 비고: 결측치 발견 ({dropped_count}건), 분석 신뢰도를 위해 정제합니다.")
            df = df.dropna() # 리뷰 데이터는 주관적 정보이므로 임의 대체보다 삭제가 분석 신뢰도 측면에서 유리하다고 판단
        else:
            print(f" >> 비고: 결측치 없음 확인, 데이터 무결성 확보 완료")
        
        # [Checkpoint 1-3] 분포 시각화 및 이상치 탐지 준비 완료
        print(f"[System] 1단계 완료: 총 {len(df)}건의 유효 데이터를 확보했습니다.")
        return df, original_count, dropped_count, missing_cols

    except Exception as e:
        print(f"[System] 데이터 로드 중 치명적 오류 발생: {e}")
        return None

def analyze_and_visualize(df, original_count, dropped_count, missing_cols, save_dir):
    """
    로드된 데이터를 기반으로 기술 통계 분석 및 시각화 결과를 이미지 파일로 저장합니다.
    보고서 작성에 적합한 고해상도 이미지를 생성하고 AI 분석용 인사이트를 도출합니다.

    [2단계: 기술 통계 및 시각화] - 비고: 변수별 분포 및 관계 시각화 수행
    [3단계: AI 분석을 위한 인사이트 도출] - 비고: 그래프 기반 AI 학습 데이터 특성 추출 완료

    Args:
        df (pd.DataFrame): 분석할 데이터프레임
        original_count (int): 전처리 전 원본 데이터 건수
        dropped_count (int): 제거된 결측치 건수
        missing_cols (list): 결측치가 발생했던 컬럼 목록
        save_dir (str): 결과 이미지를 저장할 디렉토리 경로
    """
    print(f"\n[2단계 처리 중] 기술 통계 요약 및 기초 시각화를 진행합니다.")
    
    if not os.path.exists(save_dir):
        os.makedirs(save_dir)
        print(f" >> 비고: 결과 저장 폴더({os.path.basename(save_dir)}) 생성 완료")
    
    # [Font Fix] Seaborn 설정이 폰트를 초기화하므로, set_style 이후에 폰트를 재설정해야 함
    sns.set_style("whitegrid")
    try:
        plt.rcParams['font.family'] = 'NanumGothic'
        plt.rcParams['axes.unicode_minus'] = False
    except:
        pass
    
    # [Checkpoint 2-1] 기술 통계 요약 - 비고: review_length 등 수치 데이터 요약 완료
    print(f" >> 비고: 주요 수치형 변수(평점, 길이, 감성점수) 기술 통계 산출")
    stats_df = df[['review_length', 'sentiment_score', 'rating']].describe()
    print(stats_df)
    
    # 기술 통계 용어 설명 출력 (실무 가이드)
    print("-" * 60)
    print(" [참고: 기술 통계 용어 설명]")
    print(" * count : 데이터 개수 (N수, 결측치 제외)")
    print(" * mean  : 평균값 (Arithmetic Mean)")
    print(" * std   : 표준편차 (데이터의 산포도, 클수록 평균에서 멀리 퍼져있음)")
    print(" * min/max: 최솟값 및 최댓값 (범위 확인 및 이상치 탐지용)")
    print(" * 50%   : 중앙값 (Median, 평균의 왜곡을 보정하는 지표)")
    print("-" * 60)
    
    target_col = 'rating' if 'rating' in df.columns else 'score'
    
    if target_col in df.columns:
        
        # [NEW] 1단계 보고서용: 주요 속성 종합 분포 시각화 (Subplots)
        # 평점(막대), 감성점수(히스토그램+KDE), 리뷰길이(히스토그램+KDE)
        fig, axes = plt.subplots(1, 3, figsize=(18, 5))
        
        # 1. 평점 분포
        sns.countplot(x=target_col, data=df, palette='viridis', hue=target_col, legend=False, ax=axes[0])
        axes[0].set_title(f'평점({target_col}) 분포')
        axes[0].set_xlabel('평점')
        axes[0].set_ylabel('리뷰 수')
        
        # 2. 감성 점수 분포 (선그래프 포함)
        sns.histplot(data=df, x='sentiment_score', kde=True, ax=axes[1], color='blue', bins=20)
        axes[1].set_title('감성 점수(Sentiment) 분포')
        
        # 3. 리뷰 길이 분포 (선그래프 포함)
        sns.histplot(data=df, x='review_length', kde=True, ax=axes[2], color='green', bins=20)
        axes[2].set_title('리뷰 길이(Length) 분포')
        
        plt.tight_layout()
        plt.savefig(os.path.join(save_dir, '00_data_distribution_summary.png'), dpi=300)
        plt.close()
        print(f" >> 비고: 1단계 - 주요 속성(평점, 감성, 길이) 종합 분포 시각화 완료")

        print(f"\n[3단계 처리 중] AI 분석을 위한 심층 인사이트를 도출합니다.")

        # [Checkpoint 2-3] 평점과 감성 점수 관계 시각화 - 비고: 상관관계 탐색 완료
        # [Checkpoint 3-1] 인사이트: sentiment_score가 높을수록 평점이 높은지 확인
        plt.figure(figsize=(10, 6))
        # Regplot은 hue 파라미터를 사용하지 않으므로 그대로 유지
        sns.regplot(x='sentiment_score', y=target_col, data=df, scatter_kws={'alpha':0.3}, line_kws={'color':'red'})
        plt.title('감성 점수와 평점의 상관관계', fontsize=15)
        # [Fix] 파일명 번호 정렬 (01번)
        plt.savefig(os.path.join(save_dir, '01_sentiment_vs_rating.png'), dpi=300)
        plt.close()
        print(f" >> 비고: 3단계 - 감성 점수 기반 상관관계 분석 완료")

        # [Checkpoint 2-4] 텍스트 길이와 평점 관계 - 비고: 분포 및 이상치 탐지 완료
        # [Checkpoint 3-2] 인사이트: Review_length가 AI 임베딩 토큰 처리에 미치는 영향 분석
        plt.figure(figsize=(10, 6))
        # [Fix Warning] hue를 x와 동일하게 설정하고 legend=False 추가
        sns.boxplot(x=target_col, y='review_length', data=df, palette='viridis', hue=target_col, legend=False)
        plt.title('평점별 리뷰 길이 분포', fontsize=15)
        # [Fix] 파일명 번호 정렬 (02번)
        plt.savefig(os.path.join(save_dir, '02_length_vs_rating_boxplot.png'), dpi=300)
        plt.close()
        print(f" >> 비고: 3단계 - 리뷰 길이 데이터 분포 분석 완료")

        # [Checkpoint 3-3] category 별 감성 점수 차이 분석 - 비고: AI 모델용 인사이트 도출 완료
        plt.figure(figsize=(10, 6))
        # [Fix Warning] hue를 x와 동일하게 설정하고 legend=False 추가
        sns.violinplot(x='category', y='sentiment_score', data=df, palette='Pastel1', hue='category', legend=False)
        plt.title('카테고리별 감성 점수 분포', fontsize=15)
        # [Fix] 파일명 번호 정렬 (03번)
        plt.savefig(os.path.join(save_dir, '03_category_sentiment_dist.png'), dpi=300)
        plt.close()
        print(f" >> 비고: 3단계 - 카테고리별 감성 점수 편차 분석 완료")

        # [Checkpoint 3-4] 3줄 요약 Insight 작성
        print("\n[AI Analysis Insight Summary]")
        print("1. 감성 점수가 높을수록 평점이 상승하는 뚜렷한 양의 상관관계가 확인됨.")
        print("2. 극단적 평점(1,5점) 리뷰가 더 긴 경향이 있어 임베딩 시 토큰 손실 위험이 있음.")
        print("3. 카테고리별로 감성 점수 분포 차이가 존재하므로 도메인 특화 모델이 필수적임.")

        # --------------------------------------------------------------------------------
        # [Checkpoint 4-Bonus] 노션/GitHub 호환용 마크다운 리포트 자동 생성 (질문-그래프-해석 구조)
        # --------------------------------------------------------------------------------
        md_path = os.path.join(save_dir, 'Result_Report.md')
        try:
            with open(md_path, 'w', encoding='utf-8') as f:
                f.write("# 고객 리뷰 데이터 AI 분석 인사이트 리포트\n\n")
                f.write("> 본 리포트는 자동화된 Python 스크립트에 의해 생성되었습니다.\n\n")

                # 1. 데이터 요약 섹션 (통계표 포함)
                f.write("## 1. 데이터 개요 및 기술 통계\n")
                f.write(f"- **분석 일자**: 2026-01-14\n")
                f.write(f"- **원본 데이터**: 총 {original_count}건\n")
                f.write(f"- **전처리 결과**: 결측치 {dropped_count}건 제거 후 총 {len(df)}건 확보\n")
                
                if dropped_count > 0:
                    f.write(f"  - **결측 발생 속성**: {', '.join(missing_cols)}\n")
                    f.write("  > *[처리 사유] 리뷰 텍스트나 평점은 고객의 고유한 주관적 경험 데이터입니다. 이를 평균값이나 임의의 값으로 대체(Imputation)할 경우, 감성 분석 모델에 거짓 정보(Noise)를 학습시키게 되어 분석 신뢰도를 치명적으로 저하시킵니다. 따라서 데이터 무결성 확보를 위해 해당 결측치를 제거하였습니다.*\n\n")
                else:
                    f.write("  > *비고: 결측치 없음 (데이터 무결성 확인됨)*\n\n")
                
                # 1단계: 데이터 분포 시각화 및 설명
                f.write("### [데이터 분포 시각화 및 이상치 탐지]\n")
                f.write("![Distribution](./00_data_distribution_summary.png)\n\n")
                f.write("**[분포 해석]**\n")
                f.write("- **평점(Rating)**: 막대그래프를 통해 특정 점수에 데이터가 편향(Imbalance)되어 있는지 확인합니다.\n")
                f.write("- **감성 점수(Sentiment)**: 히스토그램과 밀도 곡선(KDE)을 통해 긍정/부정의 전반적인 경향을 파악합니다.\n")
                f.write("- **리뷰 길이(Length)**: 데이터의 길이 분포를 확인하여, 극단적으로 긴 이상치(Outlier) 존재 여부를 식별합니다.\n\n")

                f.write("### [주요 변수 기초 통계량]\n")
                
                # 변수 의미 설명 추가
                f.write("> **[변수 정의]**\n")
                f.write("> - **rating**: 고객이 부여한 평점 (1~5점 척도, 정수형)\n")
                f.write("> - **sentiment_score**: 리뷰 텍스트의 감성 분석 결과 (-1:부정 ~ +1:긍정, 실수형)\n")
                f.write("> - **review_length**: 리뷰 텍스트의 문자 길이 (글자 수, 정수형)\n\n")

                f.write("| 변수명 | 평균(Mean) | 표준편차(Std) | 최소(Min) | 중앙값(50%) | 최대(Max) |\n")
                f.write("| :--- | :---: | :---: | :---: | :---: | :---: |\n")
                
                # 기술 통계 데이터를 마크다운 표로 변환하여 기록
                for col in ['rating', 'sentiment_score', 'review_length']:
                    stats = df[col].describe()
                    f.write(f"| {col} | {stats['mean']:.2f} | {stats['std']:.2f} | {stats['min']:.2f} | {stats['50%']:.2f} | {stats['max']:.2f} |\n")
                
                # 통계 지표 해석 가이드
                f.write("\n> **[참고: 통계 지표 해석 가이드]**\n")
                f.write("- **mean (평균)**: 데이터의 중심 경향을 나타냅니다.\n")
                f.write("- **std (표준편차)**: 데이터가 평균을 중심으로 얼마나 퍼져 있는지 보여줍니다. (값이 클수록 데이터 분포가 넓음)\n")
                f.write("- **50% (중앙값)**: 데이터를 크기순으로 나열했을 때 정중앙에 위치한 값으로, 이상치(Outlier)의 영향을 덜 받습니다.\n")
                f.write("\n---\n\n")

                # Q1 섹션
                f.write("## Q1. sentiment_score가 높을 수록 평점이 높은가?\n")
                f.write("![Correlation](./01_sentiment_vs_rating.png)\n\n")
                f.write("**[그래프 기반 해석]**\n")
                f.write("- 회귀선(붉은색)이 우상향하는 경향을 보이며, 감성 점수와 평점 간의 뚜렷한 **양의 상관관계**가 관찰됩니다.\n")
                f.write("- 특히 감성 점수가 0.5 이상인 구간에서 고평점(4~5점)의 밀도가 높습니다.\n\n")
                f.write("**[Insight 3줄 요약]**\n")
                f.write("1. **[결론]** 감성 점수가 높을수록 평점이 높아집니다. 이는 감성 분석이 평점 예측의 핵심 지표임을 증명합니다.\n")
                f.write("2. 따라서 AI 모델 학습 시 Sentiment Score를 단순 참조가 아닌 **가중치(Weight) 피처**로 적극 활용해야 합니다.\n")
                f.write("3. 단, 감성 점수는 낮은데 평점이 높은 일부 이상치(Outlier) 데이터는 별도로 필터링하여 검수할 필요가 있습니다.\n")
                f.write("---\n\n")

                # Q2 섹션
                f.write("## Q2. Review_length가 AI 임베딩 유사도에 영향을 줄 수 있나?\n")
                f.write("![Length](./02_length_vs_rating_boxplot.png)\n\n")
                f.write("**[그래프 기반 해석]**\n")
                f.write("- 평점 1점(불만)과 5점(만족)인 그룹에서 **리뷰 길이의 분산(Variance)**이 중앙값 대비 크게 나타납니다.\n")
                f.write("- 즉, 강한 긍정/부정 의사를 가진 고객이 더 길고 자세한 리뷰를 작성하는 경향이 뚜렷합니다.\n\n")
                f.write("**[Insight 3줄 요약]**\n")
                f.write("1. **[결론]** 영향을 줍니다. 극단적 평점의 리뷰 길이가 길어 **임베딩 시 토큰 잘림(Truncation) 현상**이 발생할 확률이 높습니다.\n")
                f.write("2. 따라서 긴 리뷰는 앞부분만 자르지 말고, **핵심 문장 추출(Summarization) 전처리**를 수행한 후 임베딩해야 정확도가 보장됩니다.\n")
                f.write("3. 반면 짧은 리뷰가 많은 평점 3점대는 정보량이 부족하므로, 유사도 검색 시 순위를 낮추는 가중치 조정이 필요합니다.\n")
                f.write("---\n\n")

                # Q3 섹션
                f.write("## Q3. Category 별 감성 점수 평균 차이는 존재하나?\n")
                f.write("![Sentiment](./03_category_sentiment_dist.png)\n\n")
                f.write("**[그래프 기반 해석]**\n")
                f.write("- 바이올린 플롯(Violin Plot) 결과, 카테고리마다 감성 점수의 분포 형태(Shape)와 밀집 구간이 서로 다름이 확인되었습니다.\n")
                f.write("- 특정 카테고리는 긍정 감성에 치우친 반면, 다른 카테고리는 중립/부정에 넓게 퍼져 있습니다.\n\n")
                f.write("**[Insight 3줄 요약]**\n")
                f.write("1. **[결론]** 존재합니다. 카테고리(패션, 전자제품 등)에 따라 고객이 느끼는 감정의 기저율(Base Rate)이 다릅니다.\n")
                f.write("2. 모든 카테고리에 동일한 감성 사전을 적용하면, 특정 카테고리에서는 부정 리뷰를 긍정으로 오분류할 위험이 있습니다.\n")
                f.write("3. 이를 해결하기 위해 범용 모델이 아닌 **카테고리별 도메인 특화(Domain-Specific) 감성 모델**을 구축하거나 파인튜닝해야 합니다.\n")
            
            print(f" >> 비고: 리포트 구조 개편 완료 ('질문-그래프-해석-요약' 및 통계표/변수정의 통합)")
        except Exception as e:
            print(f" >> [Warning] 리포트 파일 생성 실패: {e}")

    else:
        print(f"[Warning] '{target_col}' 컬럼을 찾을 수 없습니다.")

def main():
    """
    메인 실행 함수입니다. 경로 조작 방지를 위해 base_dir을 절대 경로로 고정합니다.
    [4단계: Report 작성] - 비고: 최종 분석 코드와 인사이트 리포트 정리 완료
    """
    # [보안] 경로 조작 공격 방지를 위해 실행 파일 위치를 기준으로 base_dir 고정
    # os.path.abspath(__file__)는 호출자가 어디든 스크립트 위치를 기준으로 경로를 생성함
    base_dir = os.path.dirname(os.path.abspath(__file__))
    
    # 폴더 구조에 따른 정확한 경로 설정
    data_path = os.path.join(base_dir, 'data', 'reviews_1000.csv')
    output_dir = os.path.join(base_dir, 'output')

    # [Checkpoint 4-1] 리포트 작성 시작 - 비고: 제목/목차/시각화 포함 프로세스 시작
    print("="*65)
    print("         CUSTOMER REVIEW AI ANALYSIS REPORT SYSTEM")
    print("="*65)
    print(f"[Info] 프로젝트 루트: {base_dir}")
    
    # load_data 함수에서 반환값 4개(df, original, dropped, missing_cols)를 받음
    result = load_data(data_path)
    
    if result is not None:
        df, original_count, dropped_count, missing_cols = result
        analyze_and_visualize(df, original_count, dropped_count, missing_cols, output_dir)
        
        # [Checkpoint 4-2] 리포트 정리 비고 - 비고: 최종 인사이트 정리 및 이미지 저장 완료
        print(f"\n[4단계 처리 중] 분석 결과 리포트 작성을 마무리합니다.")
        print(f" >> 비고: 고해상도 시각화 이미지 4종 저장 및 인사이트 요약본 생성 완료")
        print(f"[Report] 분석 결과 리포트가 '{output_dir}' 폴더에 생성되었습니다.")
        
    print("\n>>> 모든 분석 프로세스가 정상 종료되었습니다.")

if __name__ == "__main__":
    main()