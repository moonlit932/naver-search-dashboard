import streamlit as st
import pandas as pd
from typing import Dict, Any, List
from ..services.eda_processor import EdaProcessor
from ..utils.helpers import clean_html
from .charts import (
    create_category_source_bar_chart,
    create_category_text_length_hist,
    create_category_length_boxplot,
    create_category_weekday_bar_chart,
    create_category_date_timeline_chart
)

def render_category_deep_eda_tab(
    category_key: str,
    category_name: str,
    all_search_results: Dict[str, Dict[str, Dict[str, Any]]],
    keywords: List[str]
):
    """
    단일 카테고리(뉴스, 블로그, 카페 등)에 대한 5개 그래프 + 5개 표 심층 EDA 렌더링
    """
    # 1. 모든 키워드에 대한 데이터 통합 취합
    combined_rows = []
    total_channel_volume = 0

    for kw in keywords:
        cat_info = all_search_results.get(kw, {}).get(category_key, {})
        items = cat_info.get("items", [])
        total_channel_volume += cat_info.get("total", 0)
        df_kw = EdaProcessor.channel_items_to_df(items, category_key, keyword=kw)
        if not df_kw.empty:
            combined_rows.append(df_kw)

    if not combined_rows:
        st.warning(f"⚠️ {category_name}에 대해 수집된 데이터가 없습니다.")
        return

    full_df = pd.concat(combined_rows, ignore_index=True)

    # 2. 상단 요약 배너 및 KPI 메트릭
    st.markdown(f"## 📌 {category_name} 통합 탐색적 데이터 분석 (EDA)")
    st.caption(f"네이버 검색 API 실시간 수집 표본: 총 {len(full_df):,}건 분석 (전체 검색 볼륨 합계: {total_channel_volume:,}건)")

    # 상단 요약 카드 4개
    kpi_col1, kpi_col2, kpi_col3, kpi_col4 = st.columns(4)
    with kpi_col1:
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">분석 표본 수</div>
            <div class="metric-value">{:,} 건</div>
        </div>
        """.format(len(full_df)), unsafe_allow_html=True)

    with kpi_col2:
        avg_title = full_df["title_len"].mean() if "title_len" in full_df else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">평균 제목 글자수</div>
            <div class="metric-value">{:.1f} 자</div>
        </div>
        """.format(avg_title), unsafe_allow_html=True)

    with kpi_col3:
        avg_desc = full_df["desc_len"].mean() if "desc_len" in full_df else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">평균 본문 요약 글자수</div>
            <div class="metric-value">{:.1f} 자</div>
        </div>
        """.format(avg_desc), unsafe_allow_html=True)

    with kpi_col4:
        source_count = full_df["source"].nunique() if "source" in full_df else 0
        st.markdown("""
        <div class="metric-card">
            <div class="metric-label">고유 출처/작성자 수</div>
            <div class="metric-value">{:,} 곳</div>
        </div>
        """.format(source_count), unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 통계 테이블 사전 생성
    stat_tables = EdaProcessor.get_category_statistics_tables(full_df)

    # ------------------------------------------------------------------
    # PART 1: 통계 분석 테이블 5종
    # ------------------------------------------------------------------
    st.markdown("### 📋 1. 통계 분석 및 요약 표 (5종)")
    
    t_tab1, t_tab2, t_tab3, t_tab4, t_tab5 = st.tabs([
        "📊 [표 1] 기술통계량 요약",
        "🏢 [표 2] 출처/작성자 점유율 빈도표",
        "🔀 [표 3] 키워드 × 출처 교차표",
        "📅 [표 4] 요일 × 키워드 피봇테이블",
        "📐 [표 5] 본문 길이 구간별 집계표"
    ])

    with t_tab1:
        st.markdown("##### 📌 [표 1] 텍스트 메타데이터 기술통계량 (Descriptive Statistics)")
        st.caption("수집된 제목 및 본문 요약문의 표본수, 중심경향치(평균, 중앙값), 산포도(표준편차, 사분위수), 왜도(Skewness)")
        if "descriptive_stats" in stat_tables:
            st.dataframe(stat_tables["descriptive_stats"], use_container_width=True)
        else:
            st.info("통계량 산출 데이터가 부족합니다.")

    with t_tab2:
        st.markdown("##### 🏢 [표 2] 상위 출처 / 채널 / 작성자 점유율 빈도표 (Frequency Table)")
        st.caption(f"{category_name} 검색 결과에 가장 빈번하게 노출되는 상위 출처와 전체 표본 대비 점유율")
        if "source_frequency" in stat_tables:
            st.dataframe(stat_tables["source_frequency"], use_container_width=True)
        else:
            st.info("출처 정보가 없습니다.")

    with t_tab3:
        st.markdown("##### 🔀 [표 3] 검색어 × 주요 출처 교차표 (Cross-tabulation)")
        st.caption("상위 주요 출처별로 어떤 키워드가 더 활발하게 게시되는지 교차 빈도 확인")
        if "keyword_source_crosstab" in stat_tables:
            st.dataframe(stat_tables["keyword_source_crosstab"], use_container_width=True)
        else:
            st.info("교차표 데이터가 없습니다.")

    with t_tab4:
        st.markdown("##### 📅 [표 4] 발행 요일 × 키워드 피봇 테이블 (Pivot Table)")
        st.caption("요일별(월~일) 게시물 업로드 패턴과 키워드별 분포 현황")
        if "weekday_pivot" in stat_tables:
            st.dataframe(stat_tables["weekday_pivot"], use_container_width=True)
        else:
            st.info("요일 데이터가 부족합니다.")

    with t_tab5:
        st.markdown("##### 📐 [표 5] 본문 길이 구간별(단문/중문/장문) 집계 요약표")
        st.caption("글자 수 구간에 따른 게시물 건수와 제목 평균 길이 비교")
        if "length_segment_summary" in stat_tables:
            st.dataframe(stat_tables["length_segment_summary"], use_container_width=True)
        else:
            st.info("구간 데이터가 없습니다.")

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # PART 2: 심층 시각화 차트 5종 (파이 차트 전면 배제)
    # ------------------------------------------------------------------
    st.markdown("### 📈 2. 심층 시각화 차트 (5종 - 파이차트 제외)")

    # 2열 또는 풀와이드 레이아웃으로 5개 차트 렌더링
    chart_col1, chart_col2 = st.columns(2)

    with chart_col1:
        st.plotly_chart(
            create_category_source_bar_chart(full_df, category_name, chart_height=520),
            use_container_width=True,
            key=f"{category_key}_chart_source"
        )

    with chart_col2:
        st.plotly_chart(
            create_category_text_length_hist(full_df, category_name, chart_height=520),
            use_container_width=True,
            key=f"{category_key}_chart_length_hist"
        )

    chart_col3, chart_col4 = st.columns(2)

    with chart_col3:
        st.plotly_chart(
            create_category_length_boxplot(full_df, category_name, chart_height=520),
            use_container_width=True,
            key=f"{category_key}_chart_boxplot"
        )

    with chart_col4:
        st.plotly_chart(
            create_category_weekday_bar_chart(full_df, category_name, chart_height=520),
            use_container_width=True,
            key=f"{category_key}_chart_weekday"
        )

    # 5번째 차트: 전체 폭으로 시원하게 시계열/타임라인 차트 배치
    st.plotly_chart(
        create_category_date_timeline_chart(full_df, category_name, chart_height=520),
        use_container_width=True,
        key=f"{category_key}_chart_timeline"
    )

    # 6번째 차트: 불용어가 필터링된 카테고리별 핵심 연관 단어 TOP 20 출현 빈도 차트
    all_cat_texts = full_df["title"].tolist() + full_df["description"].tolist()
    from ..utils.helpers import extract_keywords_frequency
    cat_top_words = extract_keywords_frequency(all_cat_texts, top_n=20)
    if cat_top_words:
        cat_word_df = pd.DataFrame(cat_top_words)
        from .charts import create_word_freq_bar_chart
        cat_word_df["keyword"] = category_name
        st.plotly_chart(
            create_word_freq_bar_chart(cat_word_df, category_name, chart_height=520),
            use_container_width=True,
            key=f"{category_key}_chart_words"
        )

    st.markdown("<br><hr>", unsafe_allow_html=True)

    # ------------------------------------------------------------------
    # PART 3: 원문 데이터 탐색기 & CSV 다운로드
    # ------------------------------------------------------------------
    with st.expander(f"📥 {category_name} 원문 상세 데이터 탐색 및 CSV 다운로드", expanded=False):
        st.markdown(f"**전체 표본 건수:** {len(full_df)} 건")
        
        display_cols = ["keyword", "title", "source", "pub_date", "weekday", "title_len", "desc_len", "link"]
        available_cols = [c for c in display_cols if c in full_df.columns]
        
        st.dataframe(full_df[available_cols], use_container_width=True)

        csv_bytes = full_df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            label=f"💾 {category_name} 전체 정제 데이터 CSV 다운로드",
            data=csv_bytes,
            file_name=f"naver_{category_key}_eda_data.csv",
            mime="text/csv",
            key=f"csv_dl_{category_key}"
        )
