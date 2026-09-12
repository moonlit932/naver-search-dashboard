import streamlit as st
import pandas as pd
from typing import Dict, Any, List

def render_category_views(all_search_results: Dict[str, Dict[str, Dict[str, Any]]], selected_keyword: str):
    """
    선택된 검색어의 8개 카테고리별 원문 데이터 탭 렌더링
    """
    channels = all_search_results.get(selected_keyword, {})
    if not channels:
        st.info("조회된 검색 데이터가 없습니다.")
        return

    # 8대 카테고리 탭 구성
    category_keys = ["news", "blog", "webkr", "image", "kin", "local", "cafearticle", "encyc"]
    tab_names = [f"📰 {channels[k]['name']}" if k in channels else k for k in category_keys]
    
    tabs = st.tabs(tab_names)

    for i, cat_key in enumerate(category_keys):
        cat_info = channels.get(cat_key, {})
        with tabs[i]:
            total_cnt = cat_info.get("total", 0)
            items = cat_info.get("items", [])
            st.markdown(f"**총 검색 결과 수:** `{total_cnt:,}` 건 (현재 수집: `{len(items)}` 건)")

            if not cat_info.get("success", False):
                st.error(f"데이터 조회 실패: {cat_info.get('error')}")
                continue

            if not items:
                st.write("수집된 결과가 없습니다.")
                continue

            # 이미지 카테고리 특별 처리
            if cat_key == "image":
                render_image_gallery(items)
                continue

            # 일반 텍스트 카테고리는 카드 및 데이터프레임으로 표현
            view_type = st.radio(
                "표시 형태 선택",
                ["카드 형태 보기", "테이블(데이터프레임) 보기"],
                key=f"view_type_{selected_keyword}_{cat_key}",
                horizontal=True
            )

            from ..services.eda_processor import EdaProcessor
            items_df = EdaProcessor.channel_items_to_df(items, cat_key)

            if view_type == "테이블(데이터프레임) 보기":
                st.dataframe(items_df, use_container_width=True)
                csv_data = items_df.to_csv(index=False).encode('utf-8-sig')
                st.download_button(
                    label=f"📥 {cat_info.get('name')} CSV 다운로드",
                    data=csv_data,
                    file_name=f"{selected_keyword}_{cat_key}_data.csv",
                    mime="text/csv",
                    key=f"download_{selected_keyword}_{cat_key}"
                )
            else:
                for idx, item in enumerate(items[:20]):
                    from ..utils.helpers import clean_html
                    title = clean_html(item.get("title", "제목 없음"))
                    desc = clean_html(item.get("description", "내용 없음"))
                    link = item.get("link", item.get("originallink", "#"))
                    extra_meta = []
                    if "pubDate" in item or "postdate" in item:
                        date_str = item.get("pubDate") or item.get("postdate")
                        extra_meta.append(f"📅 {date_str}")
                    if "bloggername" in item:
                        extra_meta.append(f"✍️ {item.get('bloggername')}")
                    if "cafename" in item:
                        extra_meta.append(f"☕ {item.get('cafename')}")
                    if "address" in item:
                        extra_meta.append(f"📍 {item.get('address')}")

                    with st.expander(f"{idx+1}. {title}", expanded=(idx < 3)):
                        st.markdown(f"**요약:** {desc}")
                        if extra_meta:
                            st.caption(" | ".join(extra_meta))
                        st.markdown(f"[🔗 원문 링크 바로가기]({link})")

def render_image_gallery(items: List[Dict[str, Any]]):
    """이미지 검색 결과 그리드 갤러리 렌더링"""
    cols_per_row = 4
    for i in range(0, min(len(items), 20), cols_per_row):
        cols = st.columns(cols_per_row)
        for j in range(cols_per_row):
            idx = i + j
            if idx < len(items):
                item = items[idx]
                thumb = item.get("thumbnail") or item.get("link")
                title = item.get("title", "")
                link = item.get("link", "#")
                with cols[j]:
                    if thumb:
                        st.image(thumb, use_container_width=True)
                    st.caption(f"[{title[:20]}...]({link})")
