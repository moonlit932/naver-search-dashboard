import streamlit as st
from datetime import datetime, timedelta
from typing import Tuple, List, Dict, Any
from ..utils.config import get_naver_credentials

def render_sidebar() -> Dict[str, Any]:
    """
    사이드바 설정 및 사용자 입력 컨트롤러
    """
    st.sidebar.title("🔍 네이버 마켓 인사이트")
    st.sidebar.markdown("네이버 오픈 API(검색 8종 + 데이터랩) EDA")
    st.sidebar.divider()

    # 1. API 인증 설정 (.env 기반 자동 로드)
    client_id, client_secret = get_naver_credentials()
    if not (client_id and client_secret):
        st.sidebar.error("⚠️ `.env` 파일에 `NAVER_CLIENT_ID` 및 `NAVER_CLIENT_SECRET`을 설정해 주세요.")

    # 세션 상태에 과거 검색 히스토리 리스트 초기화
    if "keyword_history" not in st.session_state:
        st.session_state.keyword_history = ["아이폰16, 갤럭시S24", "생성형 AI, 챗GPT", "크루즈 여행, 패키지 여행"]

    if "current_search_input" not in st.session_state:
        st.session_state.current_search_input = "아이폰16, 갤럭시S24"

    # 2. 검색어 입력 및 과거 검색 기록 탭
    st.sidebar.subheader("📌 분석 검색어")

    raw_keywords = st.sidebar.text_input(
        "검색어 입력 (쉼표 `,` 로 구분)",
        value=st.session_state.current_search_input,
        key="search_input_widget",
        help="비교할 검색어를 쉼표로 구분하여 최대 5개까지 입력할 수 있습니다."
    )

    # 과거 검색 기록 클릭 영역
    st.sidebar.markdown("**🕒 과거 검색 기록** (클릭 시 자동 입력)")
    
    # 최근 검색어 칩/버튼 목록 렌더링
    history_list = st.session_state.keyword_history[:5]
    for hist_item in history_list:
        if st.sidebar.button(f"🔍 {hist_item}", key=f"hist_btn_{hist_item}", use_container_width=True):
            st.session_state.current_search_input = hist_item
            st.rerun()

    keywords = [k.strip() for k in raw_keywords.split(",") if k.strip()]
    if len(keywords) > 5:
        st.sidebar.warning("데이터랩 API 제약으로 최대 5개 키워드까지만 비교됩니다.")
        keywords = keywords[:5]

    st.sidebar.divider()

    # 3. 기간 설정
    st.sidebar.subheader("📅 분석 기간 (데이터랩 트렌드)")
    preset = st.sidebar.selectbox(
        "기간 프리셋",
        ["직접 선택", "최근 1개월", "최근 3개월", "최근 6개월", "최근 1년"],
        index=2
    )

    today = datetime.today().date()
    if preset == "최근 1개월":
        start_default = today - timedelta(days=30)
        end_default = today
    elif preset == "최근 3개월":
        start_default = today - timedelta(days=90)
        end_default = today
    elif preset == "최근 6개월":
        start_default = today - timedelta(days=180)
        end_default = today
    elif preset == "최근 1년":
        start_default = today - timedelta(days=365)
        end_default = today
    else:
        start_default = today - timedelta(days=90)
        end_default = today

    date_range = st.sidebar.date_input(
        "조회 날짜 범위",
        value=(start_default, end_default),
        max_value=today
    )

    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
    else:
        start_date, end_date = start_default, end_default

    time_unit = st.sidebar.selectbox("트렌드 집계 단위", ["date", "week", "month"], index=0, format_func=lambda x: {"date": "일간", "week": "주간", "month": "월간"}[x])

    st.sidebar.divider()

    # 4. 검색 수집 옵션
    st.sidebar.subheader("⚙️ 검색 세부 옵션")
    display_count = st.sidebar.slider(
        "카테고리별 수집 건수 (최대 200건)", 
        min_value=50, 
        max_value=200, 
        value=100, 
        step=25, 
        help="기본 100건(1회 호출 최대치) 수집하며, 100건 초과 시 자동 페이지네이션(Start 101~)을 통해 최대 200건의 풍부한 표본을 수집합니다."
    )
    sort_option = st.sidebar.selectbox("검색 정렬 방식", ["sim", "date"], format_func=lambda x: "정확도/유사도순 (sim)" if x == "sim" else "최신순 (date)")

    # 분석 실행 버튼
    run_button = st.sidebar.button("🚀 인사이트 분석 시작", type="primary", use_container_width=True)

    return {
        "client_id": client_id,
        "client_secret": client_secret,
        "raw_keywords_str": raw_keywords,
        "keywords": keywords,
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "time_unit": time_unit,
        "display_count": display_count,
        "sort_option": sort_option,
        "run_button": run_button
    }
