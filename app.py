import streamlit as st
import pandas as pd
from src.components.sidebar import render_sidebar
from src.components.charts import (
    create_trend_line_chart, 
    create_channel_bar_chart, 
    create_word_freq_bar_chart,
    create_word_cloud_scatter_chart
)
from src.components.category_eda_view import render_category_deep_eda_tab
from src.components.data_views import render_category_views
from src.api.client import NaverApiClient
from src.api.search import NaverSearchService
from src.api.datalab import NaverDatalabService
from src.services.eda_processor import EdaProcessor
from src.services.trend_service import TrendService

# 1. Streamlit 와이드 페이지 설정
st.set_page_config(
    page_title="Naver Market Insight & Deep EDA",
    page_icon="🔎",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 2. 화면 전체를 채우는 볼드하고 시원한 커스텀 스타일 (폰트/차트 확대)
st.markdown("""
<style>
    /* 전체 여백 최적화 및 폰트 크기 확대 (상단바 가림 방지 여백 확보) */
    .block-container {
        padding-top: 4.2rem !important;
        padding-bottom: 3rem !important;
        padding-left: 2.5rem !important;
        padding-right: 2.5rem !important;
        max-width: 98% !important;
    }
    .main-title {
        font-size: 2.5rem !important;
        font-weight: 800;
        color: #03C75A;
        letter-spacing: -0.5px;
        margin-top: 0.5rem;
        margin-bottom: 0.4rem;
        line-height: 1.3;
    }
    .sub-title {
        color: #4b5563;
        font-size: 1.2rem !important;
        margin-bottom: 1.8rem;
        font-weight: 500;
    }
    /* 큼직하고 선명한 메트릭 카드 */
    .metric-card {
        background: linear-gradient(135deg, #ffffff 0%, #f9fafb 100%);
        border-radius: 12px;
        padding: 20px 22px;
        border-left: 6px solid #03C75A;
        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.05);
        margin-bottom: 15px;
    }
    .metric-label {
        font-size: 1.05rem;
        color: #6b7280;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .metric-value {
        font-size: 2.2rem;
        font-weight: 800;
        color: #111827;
        line-height: 1.2;
    }
    .metric-delta {
        font-size: 0.95rem;
        color: #059669;
        font-weight: 600;
        margin-top: 4px;
    }
    /* 책갈피/인덱스 탭 형태의 고가독성 디자인 */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px !important;
        border-bottom: 3px solid #03C75A !important;
        padding-bottom: 2px !important;
        margin-bottom: 25px !important;
    }
    .stTabs [data-baseweb="tab"] {
        height: 56px !important;
        white-space: pre-wrap !important;
        font-size: 1.3rem !important;
        font-weight: 800 !important;
        padding: 10px 24px !important;
        background-color: #f1f5f9 !important;
        border: 2px solid #cbd5e1 !important;
        border-bottom: none !important;
        border-radius: 12px 12px 0 0 !important;
        color: #475569 !important;
        transition: all 0.2s ease-in-out !important;
        box-shadow: 0 -2px 6px rgba(0, 0, 0, 0.04) !important;
    }
    /* 마우스 호버 시 책갈피 들뜸 효과 */
    .stTabs [data-baseweb="tab"]:hover {
        background-color: #e2e8f0 !important;
        color: #0f172a !important;
        transform: translateY(-2px) !important;
    }
    /* 활성화(선택)된 책갈피 탭 */
    .stTabs [aria-selected="true"] {
        background: linear-gradient(180deg, #ffffff 0%, #f0fdf4 100%) !important;
        color: #03C75A !important;
        border: 2px solid #03C75A !important;
        border-bottom: 4px solid #ffffff !important;
        margin-bottom: -3px !important;
        font-weight: 900 !important;
        box-shadow: 0 -4px 10px rgba(3, 199, 90, 0.15) !important;
    }
    /* 탭 내부 텍스트 및 이모지 크기 */
    .stTabs [data-baseweb="tab"] div {
        font-size: 1.3rem !important;
    }
    /* 데이터프레임 폰트 및 가독성 개선 */
    .stDataFrame {
        font-size: 1.05rem !important;
    }
    /* 사이드바 글자 크기 최적화 (너무 크지 않고 깔끔한 폰트 크기) */
    [data-testid="stSidebar"] {
        font-size: 0.95rem !important;
    }
    [data-testid="stSidebar"] .stMarkdown p {
        font-size: 0.95rem !important;
        font-weight: 400 !important;
    }
    [data-testid="stSidebar"] label {
        font-size: 0.95rem !important;
        font-weight: 600 !important;
        color: #374151 !important;
    }
    [data-testid="stSidebar"] input, 
    [data-testid="stSidebar"] select, 
    [data-testid="stSidebar"] .stSelectbox div,
    [data-testid="stSidebar"] .stDateInput div {
        font-size: 0.92rem !important;
    }
    [data-testid="stSidebar"] button {
        font-size: 1.05rem !important;
        font-weight: 700 !important;
        padding: 0.5rem 0.8rem !important;
    }
    [data-testid="stSidebar"] h1, 
    [data-testid="stSidebar"] h2, 
    [data-testid="stSidebar"] h3 {
        font-size: 1.15rem !important;
        font-weight: 700 !important;
    }
    [data-testid="stSidebar"] .stCaption {
        font-size: 0.85rem !important;
    }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🔎 네이버 마켓 인사이트 & 카테고리별 심층 EDA 대시보드</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">공식 네이버 오픈 API 기반 데이터랩 시계열 트렌드 및 채널별(뉴스·블로그·카페·웹문서·백과사전) 5종 그래프 + 5종 통계표 정밀 분석</div>', unsafe_allow_html=True)

# 3. 사이드바 렌더링
params = render_sidebar()

# 세션 상태 초기화 (데이터 캐싱)
if "analysis_data" not in st.session_state:
    st.session_state.analysis_data = None

# 4. 분석 실행 트리거
if params["run_button"]:
    if not params["client_id"] or not params["client_secret"]:
        st.error("⚠️ 네이버 API Client ID와 Client Secret을 입력하거나 `.env` 파일에 설정해 주세요!")
        st.stop()

    if not params["keywords"]:
        st.warning("⚠️ 쉼표로 구분된 최소 1개 이상의 검색어를 입력해 주세요.")
        st.stop()

    # 검색어 히스토리 실시간 업데이트
    raw_input_str = params.get("raw_keywords_str", "").strip()
    if raw_input_str:
        if "keyword_history" not in st.session_state:
            st.session_state.keyword_history = []
        if raw_input_str in st.session_state.keyword_history:
            st.session_state.keyword_history.remove(raw_input_str)
        st.session_state.keyword_history.insert(0, raw_input_str)
        st.session_state.keyword_history = st.session_state.keyword_history[:8]

    client = NaverApiClient(params["client_id"], params["client_secret"])
    search_service = NaverSearchService(client)
    datalab_service = NaverDatalabService(client)

    with st.spinner("⏳ 네이버 API에서 데이터를 수집하고 분석하는 중입니다..."):
        try:
            # 1) 8대 카테고리 검색 결과 수집
            all_search_results = {}
            for kw in params["keywords"]:
                all_search_results[kw] = search_service.search_all_categories(
                    query=kw,
                    display=params["display_count"],
                    sort=params["sort_option"]
                )

            # 2) 데이터랩 트렌드 수집
            keyword_groups = [{"groupName": kw, "keywords": [kw]} for kw in params["keywords"]]
            trend_raw = datalab_service.get_search_trend(
                start_date=params["start_date"],
                end_date=params["end_date"],
                time_unit=params["time_unit"],
                keywords_groups=keyword_groups
            )
            trend_df = TrendService.parse_datalab_response(trend_raw)

            # 3) EDA 데이터프레임 가공
            channel_df = EdaProcessor.build_channel_summary_df(all_search_results)
            words_df = EdaProcessor.extract_top_words_df(all_search_results, top_n=20)

            # 세션에 저장
            st.session_state.analysis_data = {
                "keywords": params["keywords"],
                "start_date": params["start_date"],
                "end_date": params["end_date"],
                "all_search_results": all_search_results,
                "trend_df": trend_df,
                "channel_df": channel_df,
                "words_df": words_df
            }
            st.success("✅ 데이터 수집 및 분석이 완료되었습니다!")

        except Exception as e:
            st.error(f"❌ 데이터 수집 중 오류가 발생했습니다: {str(e)}")

# 5. 데이터 시각화 렌더링
data = st.session_state.analysis_data

if data:
    keywords = data["keywords"]
    channel_df = data["channel_df"]
    trend_df = data["trend_df"]
    words_df = data["words_df"]
    all_search_results = data["all_search_results"]

    # 1) 상단 메트릭 요약 배너 (대형 카드 스타일)
    st.markdown("### 📊 키워드별 전체 채널 총 검색 결과 수 (Total Volume)")
    kpi_cols = st.columns(len(keywords))
    for idx, kw in enumerate(keywords):
        kw_total = channel_df[channel_df["keyword"] == kw]["total_count"].sum()
        with kpi_cols[idx]:
            st.markdown(f"""
            <div class="metric-card">
                <div class="metric-label">검색어: {kw}</div>
                <div class="metric-value">{kw_total:,} 건</div>
                <div class="metric-delta">8개 채널 전체 합계</div>
            </div>
            """, unsafe_allow_html=True)

    st.markdown("<br>", unsafe_allow_html=True)

    # 2) 전용 대시보드 탭 구성: 시계열 트렌드 종합 + 키워드 워드클라우드 + 5대 핵심 카테고리 개별 심층 EDA + 원문 탐색
    tab_trend, tab_cloud, tab_news, tab_blog, tab_cafe, tab_web, tab_encyc, tab_raw = st.tabs([
        "📈 검색어 시계열 트렌드 (데이터랩)",
        "☁️ 연관 키워드 워드클라우드 (TOP 20)",
        "📰 뉴스 심층 EDA",
        "✍️ 블로그 심층 EDA",
        "☕ 카페글 심층 EDA",
        "🌐 웹문서 심층 EDA",
        "📚 백과사전 심층 EDA",
        "🔍 기타 채널 및 원문 탐색"
    ])

    # -------------------------------------------------------------
    # TAB 1: 고가독성 시계열 트렌드 분석
    # -------------------------------------------------------------
    with tab_trend:
        st.subheader("📈 네이버 데이터랩 시계열 검색 트렌드 정밀 분석")
        st.caption(f"분석 기간: {data['start_date']} ~ {data['end_date']} | 상대 검색 관심도 지수(0~100)")

        # 시계열 요약 KPI 카드 (최고점 도달일, 평균 지수, 변동성)
        if not trend_df.empty:
            kw_trend_cols = [c for c in trend_df.columns if c != "date"]
            trend_kpi_cols = st.columns(len(kw_trend_cols))
            for i, kw in enumerate(kw_trend_cols):
                series = trend_df[kw]
                max_val = series.max()
                max_date = trend_df.loc[series.idxmax(), "date"].strftime("%Y-%m-%d") if not series.empty else "-"
                mean_val = series.mean()
                with trend_kpi_cols[i]:
                    st.markdown(f"""
                    <div class="metric-card" style="border-left-color: #4F46E5;">
                        <div class="metric-label">{kw} 검색 지수 요약</div>
                        <div class="metric-value">{max_val:.1f} <span style="font-size:1.1rem; color:#6b7280;">(최고치)</span></div>
                        <div class="metric-delta">📅 최고 도달일: {max_date} | 평균: {mean_val:.1f}</div>
                    </div>
                    """, unsafe_allow_html=True)

            # 시계열 인터랙티브 컨트롤 옵션
            ctrl_col1, ctrl_col2 = st.columns([1, 3])
            with ctrl_col1:
                show_ma = st.checkbox("7일 이동평균선(MA-7) 함께 보기", value=True, help="일간 변동성 노이즈를 완화하고 중장기 추세를 더 선명하게 파악합니다.")
            with ctrl_col2:
                chart_height = st.slider("차트 높이 조절 (px)", min_value=450, max_value=850, value=600, step=50)

            # 고가독성 시계열 차트 렌더링
            fig_trend = create_trend_line_chart(trend_df, show_ma=show_ma, ma_window=7, chart_height=chart_height)
            st.plotly_chart(fig_trend, use_container_width=True, key="main_trend_chart")

            # 시계열 기술통계 요약표
            st.markdown("##### 📋 [시계열 통계] 키워드별 검색 지수 기술통계량")
            trend_stats = trend_df[kw_trend_cols].describe().T
            trend_stats.rename(columns={
                "count": "관측일수",
                "mean": "평균 지수",
                "std": "표준편차(변동성)",
                "min": "최저 지수",
                "25%": "1사분위(25%)",
                "50%": "중앙값",
                "75%": "3사분위(75%)",
                "max": "최고 지수"
            }, inplace=True)
            # 변동계수(CV = std/mean)
            trend_stats["변동계수(CV)"] = (trend_stats["표준편차(변동성)"] / trend_stats["평균 지수"]).round(2)
            st.dataframe(trend_stats.round(1), use_container_width=True)

            with st.expander("📄 시계열 원본 데이터 테이블 보기"):
                st.dataframe(trend_df, use_container_width=True)

        st.divider()
        st.subheader("📊 8대 카테고리 전체 볼륨 비교")
        fig_channel = create_channel_bar_chart(channel_df, chart_height=520)
        st.plotly_chart(fig_channel, use_container_width=True, key="main_channel_chart")

        if not channel_df.empty:
            pivot_df = channel_df.pivot(index="channel_name", columns="keyword", values="total_count")
            st.markdown("##### 🔀 채널 × 키워드 교차 집계표")
            st.dataframe(pivot_df, use_container_width=True)

    # -------------------------------------------------------------
    # TAB: 연관 키워드 가중치 워드클라우드 & 텍스트 심층 EDA (TOP 20)
    # -------------------------------------------------------------
    with tab_cloud:
        st.subheader("☁️ 연관 키워드 워드클라우드 & 어휘 통계 심층 EDA (TOP 20)")
        st.caption("언급량과 검색 데이터 내 출현 빈도수에 비례하여 글자 크기가 달라지는 다크 모드 워드클라우드와 5대 통계표 & 5대 그래프 분석입니다.")

        col_kw_select, _ = st.columns([2, 2])
        with col_kw_select:
            selected_kw_cloud = st.selectbox("분석 대상 검색어 선택", keywords, key="cloud_kw_select")

        # 대상 키워드의 TOP 20 단어 데이터 추출
        kw_words_all = words_df[words_df["keyword"] == selected_kw_cloud].sort_values("count", ascending=False).copy()
        top20_df = kw_words_all.head(20).copy().reset_index(drop=True)
        top20_df["word_len"] = top20_df["word"].apply(len)
        total_top_mentions = top20_df["count"].sum()
        top20_df["share_pct"] = (top20_df["count"] / total_top_mentions * 100).round(1)
        top20_df["cum_share"] = top20_df["share_pct"].cumsum().round(1)

        # 1) 메인 시각화: 고대비 다크 모드 워드클라우드 (글자 크기 가변)
        fig_cloud = create_word_cloud_scatter_chart(words_df, selected_kw_cloud, chart_height=600)
        st.plotly_chart(fig_cloud, use_container_width=True, key=f"cloud_chart_{selected_kw_cloud}")

        st.markdown("<br><hr>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # PART 1: 키워드 EDA 통계 분석 표 5종
        # -------------------------------------------------------------
        st.markdown("### 📋 1. 연관 키워드 통계 분석 및 요약 표 (5종)")
        w_tab1, w_tab2, w_tab3, w_tab4, w_tab5 = st.tabs([
            "📊 [표 1] 단어 출현 빈도 기술통계량",
            "🏆 [표 2] TOP 20 연관어 점유율 및 순위표",
            "📏 [표 3] 글자 길이별(음절수) 단어 집계표",
            "📈 [표 4] 언급량 집중도(파레토 20/80) 구간표",
            "🔠 [표 5] 단어 메타 상세 데이터"
        ])

        with w_tab1:
            st.markdown("##### 📌 [표 1] 상위 20개 연관어 출현 빈도 기술통계량")
            st.caption("표본수, 평균 언급량, 표준편차, 중앙값, 4분위수, 왜도(Skewness)")
            w_stats = top20_df[["count", "word_len"]].describe().T
            w_stats.rename(columns={
                "count": "표본수", "mean": "평균", "std": "표준편차",
                "min": "최소값", "25%": "1사분위(25%)", "50%": "중앙값(50%)",
                "75%": "3사분위(75%)", "max": "최대값"
            }, inplace=True)
            w_stats.index = ["언급 빈도수", "단어 글자수(길이)"]
            w_stats["왜도(Skewness)"] = [top20_df["count"].skew().round(2), top20_df["word_len"].skew().round(2)]
            st.dataframe(w_stats.round(1), use_container_width=True)

        with w_tab2:
            st.markdown("##### 🏆 [표 2] TOP 20 연관 키워드 점유율 및 누적 비중")
            st.caption("상위 20개 단어 중 각 단어가 차지하는 비중과 누적 점유율 현황")
            display_t2 = top20_df[["word", "count", "share_pct", "cum_share"]].copy()
            display_t2.index = display_t2.index + 1
            display_t2.columns = ["연관 키워드", "언급/출현 건수", "TOP20 내 점유율(%)", "누적 점유율(%)"]
            display_t2["TOP20 내 점유율(%)"] = display_t2["TOP20 내 점유율(%)"].astype(str) + "%"
            display_t2["누적 점유율(%)"] = display_t2["누적 점유율(%)"].astype(str) + "%"
            st.dataframe(display_t2, use_container_width=True)

        with w_tab3:
            st.markdown("##### 📏 [표 3] 단어 글자수(음절수) 구간별 집계표")
            st.caption("2음절, 3음절, 4음절 이상의 단어 수 및 총 언급량 합계 비교")
            top20_df["len_group"] = top20_df["word_len"].apply(lambda x: f"{x}글자" if x <= 4 else "5글자 이상")
            len_summary = top20_df.groupby("len_group").agg(
                단어수=("word", "count"),
                총언급량=("count", "sum"),
                평균언급량=("count", "mean")
            ).reset_index()
            len_summary.rename(columns={"len_group": "글자수 구분"}, inplace=True)
            len_summary["평균언급량"] = len_summary["평균언급량"].round(1)
            st.dataframe(len_summary, use_container_width=True)

        with w_tab4:
            st.markdown("##### 📈 [표 4] 키워드 언급량 티어(Tier) 분포표")
            st.caption("최상위 핵심어(TOP 1~5), 주요 연관어(6~10), 일반 연관어(11~20) 구간별 집중도")
            top20_df["tier"] = ["1. 최상위 핵심어 (TOP 1~5)" if i < 5 else ("2. 주요 연관어 (TOP 6~10)" if i < 10 else "3. 서브 연관어 (TOP 11~20)") for i in range(len(top20_df))]
            tier_summary = top20_df.groupby("tier").agg(
                단어수=("word", "count"),
                총언급수=("count", "sum"),
                평균언급수=("count", "mean")
            ).reset_index()
            tier_summary.rename(columns={"tier": "키워드 그룹 티어"}, inplace=True)
            tier_summary["언급 점유비(%)"] = (tier_summary["총언급수"] / total_top_mentions * 100).round(1).astype(str) + "%"
            tier_summary["평균언급수"] = tier_summary["평균언급수"].round(1)
            st.dataframe(tier_summary, use_container_width=True)

        with w_tab5:
            st.markdown("##### 🔠 [표 5] 전체 수집 단어 원본 메타데이터 (TOP 50)")
            st.caption("필터링된 전체 연관 키워드 목록 및 CSV 다운로드")
            all_kw_display = kw_words_all.head(50).copy().reset_index(drop=True)
            all_kw_display.index = all_kw_display.index + 1
            all_kw_display.rename(columns={"word": "단어", "count": "언급 빈도"}, inplace=True)
            st.dataframe(all_kw_display[["단어", "언급 빈도"]], use_container_width=True)

        st.markdown("<br><hr>", unsafe_allow_html=True)

        # -------------------------------------------------------------
        # PART 2: 키워드 EDA 시각화 차트 5종 (파이차트 제외)
        # -------------------------------------------------------------
        st.markdown("### 📈 2. 연관 키워드 시각화 차트 (5종 - 파이차트 제외)")

        # 1 & 2열 차트
        w_col1, w_col2 = st.columns(2)
        with w_col1:
            st.plotly_chart(
                create_word_freq_bar_chart(words_df, selected_kw_cloud, chart_height=520),
                use_container_width=True,
                key=f"cloud_eda_bar_{selected_kw_cloud}"
            )

        with w_col2:
            # 트리맵 차트 (비율과 계층을 면적으로 표현)
            fig_treemap = px.treemap(
                top20_df,
                path=["tier", "word"],
                values="count",
                color="count",
                color_continuous_scale="Blues",
                title=f"🗺️ [차트 2] '{selected_kw_cloud}' 연관 키워드 트리맵(Treemap) 면적 비중",
                template="plotly_white"
            )
            fig_treemap.update_layout(height=520, margin=dict(l=20, r=20, t=60, b=20), font=dict(size=14))
            st.plotly_chart(fig_treemap, use_container_width=True, key=f"cloud_eda_treemap_{selected_kw_cloud}")

        # 3 & 4열 차트
        w_col3, w_col4 = st.columns(2)
        with w_col3:
            # 단어 글자수 히스토그램
            fig_len_hist = px.bar(
                len_summary,
                x="글자수 구분",
                y="총언급량",
                text_auto=True,
                color="글자수 구분",
                color_discrete_sequence=["#0284c7", "#06b6d4", "#10b981", "#f59e0b"],
                title=f"📏 [차트 3] 음절(글자수) 그룹별 총 언급량 비교",
                template="plotly_white"
            )
            fig_len_hist.update_layout(height=500, margin=dict(l=30, r=20, t=60, b=30), showlegend=False, font=dict(size=13))
            st.plotly_chart(fig_len_hist, use_container_width=True, key=f"cloud_eda_len_hist_{selected_kw_cloud}")

        with w_col4:
            # 언급량 박스플롯 (이상치 및 사분위)
            fig_w_box = px.box(
                top20_df,
                y="count",
                points="all",
                color_discrete_sequence=["#4F46E5"],
                labels={"count": "언급 건수"},
                title=f"📦 [차트 4] TOP 20 키워드 언급량 사분위 분포 및 이상치",
                template="plotly_white"
            )
            fig_w_box.update_layout(height=500, margin=dict(l=30, r=20, t=60, b=30), font=dict(size=13))
            st.plotly_chart(fig_w_box, use_container_width=True, key=f"cloud_eda_box_{selected_kw_cloud}")

        # 5번째 차트: 누적 점유율 파레토(Pareto) 라인+바 복합 차트
        import plotly.graph_objects as go
        fig_pareto = go.Figure()
        fig_pareto.add_trace(go.Bar(
            x=top20_df["word"],
            y=top20_df["count"],
            name="언급 건수",
            marker_color="#03C75A"
        ))
        fig_pareto.add_trace(go.Scatter(
            x=top20_df["word"],
            y=top20_df["cum_share"],
            name="누적 점유율(%)",
            yaxis="y2",
            mode="lines+markers",
            line=dict(color="#EF4444", width=3),
            marker=dict(size=7)
        ))
        fig_pareto.update_layout(
            title=f"📊 [차트 5] 연관 키워드 파레토(Pareto) 누적 점유율 곡선",
            xaxis=dict(title="연관 키워드", tickangle=-35, tickfont=dict(size=13)),
            yaxis=dict(title="언급 건수 (건)", showgrid=True, gridcolor="#f3f4f6"),
            yaxis2=dict(title="누적 점유율 (%)", overlaying="y", side="right", range=[0, 105]),
            height=540,
            margin=dict(l=30, r=30, t=60, b=40),
            template="plotly_white",
            legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1)
        )
        st.plotly_chart(fig_pareto, use_container_width=True, key=f"cloud_eda_pareto_{selected_kw_cloud}")

    # -------------------------------------------------------------
    # TAB 2: 뉴스 심층 EDA (5 Graphs + 5 Tables)
    # -------------------------------------------------------------
    with tab_news:
        render_category_deep_eda_tab("news", "📰 뉴스", all_search_results, keywords)

    # -------------------------------------------------------------
    # TAB 3: 블로그 심층 EDA (5 Graphs + 5 Tables)
    # -------------------------------------------------------------
    with tab_blog:
        render_category_deep_eda_tab("blog", "✍️ 블로그", all_search_results, keywords)

    # -------------------------------------------------------------
    # TAB 4: 카페글 심층 EDA (5 Graphs + 5 Tables)
    # -------------------------------------------------------------
    with tab_cafe:
        render_category_deep_eda_tab("cafearticle", "☕ 카페글", all_search_results, keywords)

    # -------------------------------------------------------------
    # TAB 5: 웹문서 심층 EDA (5 Graphs + 5 Tables)
    # -------------------------------------------------------------
    with tab_web:
        render_category_deep_eda_tab("webkr", "🌐 웹문서", all_search_results, keywords)

    # -------------------------------------------------------------
    # TAB 6: 백과사전 심층 EDA (5 Graphs + 5 Tables)
    # -------------------------------------------------------------
    with tab_encyc:
        render_category_deep_eda_tab("encyc", "📚 백과사전", all_search_results, keywords)

    # -------------------------------------------------------------
    # TAB 7: 기타 채널 및 원문 상세 탐색
    # -------------------------------------------------------------
    with tab_raw:
        st.subheader("🔍 기타 채널(지식iN, 지역, 이미지 등) 및 원문 탐색")
        selected_kw_for_view = st.selectbox("조회할 검색어 선택", keywords, key="view_kw_select_raw")
        render_category_views(all_search_results, selected_kw_for_view)

else:
    # 데이터가 아직 없을 때 안내 화면
    st.info("👈 왼쪽 사이드바에서 네이버 API 키를 확인하거나 입력한 후, **[🚀 인사이트 분석 시작]** 버튼을 클릭해 주세요.")
    
    st.markdown("""
    ### 🌟 대폭 개선된 주요 기능
    1. **시계열 데이터 가독성 강화**:
       - 굵은 라인(3px), 7일 이동평균선(MA-7) 토글, 최고치(Peak Point) 주석 표시, 시계열 기술통계량 제공.
    2. **화면 꽉 찬 볼드 레이아웃**:
       - 폰트/위젯/차트 높이를 600px+ 로 대폭 키워 한눈에 시원하게 분석 가능.
    3. **5대 카테고리(뉴스·블로그·카페·웹문서·백과사전) 전용 심층 EDA 탭**:
       - **각 탭마다 5개 이상 통계표**: 기술통계량, 출처 점유율표, 키워드×출처 교차표, 요일×키워드 피봇테이블, 길이 구간 집계표.
       - **각 탭마다 5개 이상 시각화 차트** (🚫 파이차트 완전 배제): 가로 막대 차트, 텍스트 길이 히스토그램, 사분위 박스플롯, 요일별 막대, 시계열 추이 차트.
       - 전 카테고리 원문 테이블 및 UTF-8 BOM CSV 다운로드 지원.
    """)

