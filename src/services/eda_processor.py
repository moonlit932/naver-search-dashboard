from typing import Dict, Any, List
import pandas as pd
from ..utils.helpers import clean_html, extract_keywords_frequency

class EdaProcessor:
    """수집된 검색 데이터를 분석 및 시각화용 데이터프레임으로 가공하는 프로세서"""

    @staticmethod
    def build_channel_summary_df(all_search_results: Dict[str, Dict[str, Dict[str, Any]]]) -> pd.DataFrame:
        """
        all_search_results 구조:
        {
          "키워드1": {
             "news": {"name": "뉴스", "total": 1200, ...},
             "blog": {"name": "블로그", "total": 5400, ...},
             ...
          },
          "키워드2": ...
        }
        반환: 키워드 및 채널별 총 결과수 DataFrame
        """
        records = []
        for keyword, channels in all_search_results.items():
            for cat_key, cat_data in channels.items():
                records.append({
                    "keyword": keyword,
                    "channel_key": cat_key,
                    "channel_name": cat_data.get("name", cat_key),
                    "total_count": cat_data.get("total", 0),
                    "items_count": len(cat_data.get("items", []))
                })
        return pd.DataFrame(records)

    @staticmethod
    def extract_top_words_df(all_search_results: Dict[str, Dict[str, Dict[str, Any]]], top_n: int = 20) -> pd.DataFrame:
        """
        모든 수집된 아이템의 title과 description에서 상위 빈도 단어 추출
        """
        records = []
        for keyword, channels in all_search_results.items():
            texts = []
            for cat_key, cat_data in channels.items():
                items = cat_data.get("items", [])
                for it in items:
                    title = it.get("title", "")
                    desc = it.get("description", "")
                    texts.append(title)
                    if desc:
                        texts.append(desc)
            
            freqs = extract_keywords_frequency(texts, top_n=top_n)
            for f in freqs:
                records.append({
                    "keyword": keyword,
                    "word": f["word"],
                    "count": f["count"]
                })
        return pd.DataFrame(records)

    @staticmethod
    def channel_items_to_df(items: List[Dict[str, Any]], category: str, keyword: str = "") -> pd.DataFrame:
        """단일 카테고리 검색 결과 아이템들을 테이블 뷰 및 EDA용 데이터프레임으로 변환 (풍부한 파생 변수 포함)"""
        if not items:
            return pd.DataFrame()

        rows = []
        for it in items:
            title = clean_html(it.get("title", ""))
            desc = clean_html(it.get("description", ""))
            link = it.get("link", it.get("originallink", ""))

            # 1) 출처/작성자 명칭 정제
            source = "기타/알수없음"
            if category == "news":
                # originallink 또는 link의 도메인 추출
                from urllib.parse import urlparse
                domain = urlparse(link).netloc.replace("www.", "")
                source = domain if domain else "뉴스제휴사"
            elif category == "blog":
                source = it.get("bloggername") or "블로거"
            elif category == "cafearticle":
                source = it.get("cafename") or "네이버카페"
            elif category == "webkr":
                from urllib.parse import urlparse
                domain = urlparse(link).netloc.replace("www.", "")
                source = domain if domain else "웹사이트"
            elif category == "encyc":
                source = "네이버 지식백과"
            elif category == "kin":
                source = "지식iN 작성자"
            elif category == "local":
                source = it.get("category", "지역업체")

            # 2) 날짜 파싱 (pubDate: RFC 822 형식 또는 postdate: YYYYMMDD)
            pub_date_raw = it.get("pubDate") or it.get("postdate") or ""
            dt_obj = None
            if pub_date_raw:
                try:
                    if len(pub_date_raw) == 8 and pub_date_raw.isdigit():
                        dt_obj = pd.to_datetime(pub_date_raw, format="%Y%m%d")
                    else:
                        dt_obj = pd.to_datetime(pub_date_raw)
                except Exception:
                    dt_obj = None

            pub_date_str = dt_obj.strftime("%Y-%m-%d") if dt_obj is not None and not pd.isna(dt_obj) else ""
            weekday_kr = ["월", "화", "수", "목", "금", "토", "일"][dt_obj.weekday()] if dt_obj is not None and not pd.isna(dt_obj) else "미상"

            title_len = len(title)
            desc_len = len(desc)

            # 길이 구간 라벨링
            if desc_len < 50:
                length_seg = "단문 (<50자)"
            elif desc_len <= 120:
                length_seg = "중문 (50~120자)"
            else:
                length_seg = "장문 (>120자)"

            rows.append({
                "keyword": keyword,
                "title": title,
                "description": desc,
                "source": source,
                "pub_date": pub_date_str,
                "weekday": weekday_kr,
                "title_len": title_len,
                "desc_len": desc_len,
                "length_seg": length_seg,
                "link": link
            })

        df = pd.DataFrame(rows)
        return df

    @staticmethod
    def get_category_statistics_tables(df: pd.DataFrame) -> Dict[str, pd.DataFrame]:
        """
        카테고리 상세 EDA를 위한 5대 통계 분석 표 생성
        1. 기술통계량 표 (Descriptive Stats)
        2. 출처/작성자 점유율 빈도표 (Frequency & Ratio)
        3. 키워드 x 출처 교차표 (Crosstab)
        4. 요일 x 키워드 피봇 테이블 (Pivot Table)
        5. 본문 길이 구간별 집계 요약표 (Segmented Summary)
        """
        tables = {}
        if df.empty:
            return tables

        # 1. 기술통계량 표 (Descriptive Stats: 제목길이, 본문길이)
        desc_cols = [c for c in ["title_len", "desc_len"] if c in df.columns]
        if desc_cols:
            stats = df[desc_cols].describe().T
            stats.rename(columns={
                "count": "표본수",
                "mean": "평균",
                "std": "표준편차",
                "min": "최소값",
                "25%": "1사분위(25%)",
                "50%": "중앙값(50%)",
                "75%": "3사분위(75%)",
                "max": "최대값"
            }, inplace=True)
            stats.index = ["제목 글자수", "본문 요약 글자수"][:len(stats)]
            # 추가 통계: 왜도(Skewness)
            stats["왜도(Skewness)"] = df[desc_cols].skew().round(2).values
            tables["descriptive_stats"] = stats.round(1)

        # 2. 상위 출처/작성자 점유율 빈도표
        if "source" in df.columns:
            source_cnt = df["source"].value_counts().reset_index()
            source_cnt.columns = ["출처/채널/작성자", "게시물 수"]
            total_items = len(df)
            source_cnt["점유율(%)"] = (source_cnt["게시물 수"] / total_items * 100).round(1).astype(str) + "%"
            source_cnt["누적 점유율(%)"] = (source_cnt["게시물 수"].cumsum() / total_items * 100).round(1).astype(str) + "%"
            tables["source_frequency"] = source_cnt.head(15)

        # 3. 키워드 x 상위 출처 교차표 (Crosstab)
        if "keyword" in df.columns and "source" in df.columns and df["keyword"].nunique() > 0:
            top_sources = df["source"].value_counts().head(8).index.tolist()
            filtered_df = df[df["source"].isin(top_sources)]
            ct = pd.crosstab(filtered_df["source"], filtered_df["keyword"], margins=True, margins_name="합계")
            tables["keyword_source_crosstab"] = ct

        # 4. 요일 x 키워드 피봇 테이블 (Pivot Table)
        if "weekday" in df.columns and "keyword" in df.columns:
            weekday_order = ["월", "화", "수", "목", "금", "토", "일", "미상"]
            pivot_week = pd.crosstab(df["weekday"], df["keyword"])
            # 요일 순서 정렬
            existing_days = [d for d in weekday_order if d in pivot_week.index]
            pivot_week = pivot_week.reindex(existing_days).fillna(0).astype(int)
            pivot_week["요일별 합계"] = pivot_week.sum(axis=1)
            tables["weekday_pivot"] = pivot_week

        # 5. 본문 길이 구간별 집계 요약표 (Segmented Summary)
        if "length_seg" in df.columns:
            seg_summary = df.groupby("length_seg").agg(
                게시물수=("title", "count"),
                평균_제목길이=("title_len", "mean"),
                평균_본문길이=("desc_len", "mean")
            ).reset_index()
            seg_summary.rename(columns={"length_seg": "본문 길이 구간"}, inplace=True)
            seg_summary["게시물 비중(%)"] = (seg_summary["게시물수"] / len(df) * 100).round(1).astype(str) + "%"
            seg_summary["평균_제목길이"] = seg_summary["평균_제목길이"].round(1)
            seg_summary["평균_본문길이"] = seg_summary["평균_본문길이"].round(1)
            tables["length_segment_summary"] = seg_summary

        return tables
