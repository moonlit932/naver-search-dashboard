import plotly.express as px
import plotly.graph_objects as go
import pandas as pd
from typing import List, Optional

# 고대비/시인성 높은 프리미엄 컬러 팔레트
PALETTE = ["#03C75A", "#4F46E5", "#F59E0B", "#EF4444", "#06B6D4", "#8B5CF6", "#EC4899", "#10B981"]

def create_trend_line_chart(
    trend_df: pd.DataFrame, 
    show_ma: bool = False, 
    ma_window: int = 7,
    chart_height: int = 580
) -> go.Figure:
    """
    고가독성 네이버 데이터랩 검색어 시계열 트렌드 차트
    - 굵은 라인 (3px) + 뚜렷한 마커
    - 기간 내 최고점(Peak Point) 자동 어노테이션
    - 7일 이동평균선(MA) 옵션 지원
    - 대형 폰트 및 통합 툴팁
    """
    if trend_df.empty or "date" not in trend_df.columns:
        fig = go.Figure()
        fig.update_layout(title="표시할 트렌드 데이터가 없습니다.", height=chart_height)
        return fig

    keywords = [c for c in trend_df.columns if c != "date"]
    fig = go.Figure()

    for idx, kw in enumerate(keywords):
        color = PALETTE[idx % len(PALETTE)]
        series = trend_df[kw]

        # 1) 원본 시계열 라인
        fig.add_trace(go.Scatter(
            x=trend_df["date"],
            y=series,
            mode="lines+markers",
            name=kw,
            line=dict(color=color, width=3),
            marker=dict(size=6, symbol="circle"),
            hovertemplate=f"<b>{kw}</b>: %{{y:.1f}}<extra></extra>"
        ))

        # 2) 이동평균선 (옵션 활성화 시)
        if show_ma and len(trend_df) >= ma_window:
            ma_series = series.rolling(window=ma_window, min_periods=1).mean()
            fig.add_trace(go.Scatter(
                x=trend_df["date"],
                y=ma_series,
                mode="lines",
                name=f"{kw} ({ma_window}일 이동평균)",
                line=dict(color=color, width=2, dash="dash"),
                opacity=0.75,
                hovertemplate=f"<b>{kw} ({ma_window}D MA)</b>: %{{y:.1f}}<extra></extra>"
            ))

        # 3) 최고점(Peak Point) 어노테이션 하이라이트
        if not series.empty and series.max() > 0:
            max_val = series.max()
            max_idx = series.idxmax()
            peak_date = trend_df.loc[max_idx, "date"]
            
            fig.add_annotation(
                x=peak_date,
                y=max_val,
                text=f"👑 {kw} 최고치: {max_val:.1f}",
                showarrow=True,
                arrowhead=2,
                arrowsize=1,
                arrowwidth=2,
                arrowcolor=color,
                ax=0,
                ay=-35,
                font=dict(size=12, color="#ffffff", family="Apple SD Gothic Neo, Malgun Gothic, sans-serif"),
                bgcolor=color,
                bordercolor=color,
                borderwidth=1,
                borderpad=4,
                opacity=0.9
            )

    fig.update_layout(
        title=dict(
            text="📈 네이버 데이터랩 일간 검색어 트렌드 추이 비교",
            font=dict(size=20, color="#1f2937", family="Apple SD Gothic Neo, Malgun Gothic, sans-serif")
        ),
        xaxis=dict(
            title=dict(text="날짜", font=dict(size=15, color="#4b5563")),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#f3f4f6",
            zeroline=False
        ),
        yaxis=dict(
            title=dict(text="상대 검색 지수 (최대 100)", font=dict(size=15, color="#4b5563")),
            tickfont=dict(size=13),
            showgrid=True,
            gridcolor="#e5e7eb",
            range=[0, 108]
        ),
        hovermode="x unified",
        hoverlabel=dict(
            bgcolor="rgba(255, 255, 255, 0.95)",
            font_size=14,
            font_family="Apple SD Gothic Neo, sans-serif"
        ),
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
            font=dict(size=14)
        ),
        height=chart_height,
        margin=dict(l=40, r=30, t=80, b=40),
        template="plotly_white",
        plot_bgcolor="#fafbfc"
    )
    return fig


def create_channel_bar_chart(channel_df: pd.DataFrame, chart_height: int = 520) -> go.Figure:
    """8개 카테고리별 검색 결과 총 건수 비교 막대 차트 (폰트 및 크기 확대)"""
    if channel_df.empty:
        fig = go.Figure()
        fig.update_layout(title="채널별 데이터가 없습니다.", height=chart_height)
        return fig

    fig = px.bar(
        channel_df,
        x="channel_name",
        y="total_count",
        color="keyword",
        barmode="group",
        text_auto=".2s",
        color_discrete_sequence=PALETTE,
        labels={"total_count": "총 검색 결과 수", "channel_name": "채널 구분", "keyword": "검색어"},
        title="📊 전체 카테고리별 검색 볼륨(Total Count) 비교",
        template="plotly_white"
    )
    fig.update_traces(
        textfont_size=13,
        textposition="outside",
        cliponaxis=False
    )
    fig.update_layout(
        title_font=dict(size=20),
        xaxis=dict(title=dict(font=dict(size=15)), tickfont=dict(size=14)),
        yaxis=dict(title=dict(font=dict(size=15)), tickfont=dict(size=13), showgrid=True, gridcolor="#f3f4f6"),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=14)),
        margin=dict(l=40, r=20, t=70, b=40),
        height=chart_height
    )
    return fig


def create_word_freq_bar_chart(word_df: pd.DataFrame, selected_keyword: str, chart_height: int = 550) -> go.Figure:
    """수집된 검색어의 주요 단어 출현 빈도 수평 막대 차트"""
    subset = word_df[word_df["keyword"] == selected_keyword].sort_values("count", ascending=True)
    if subset.empty:
        fig = go.Figure()
        fig.update_layout(title="단어 빈도 데이터가 없습니다.", height=chart_height)
        return fig

    fig = px.bar(
        subset,
        x="count",
        y="word",
        orientation="h",
        labels={"count": "출현 빈도수", "word": "단어"},
        title=f"🔤 '{selected_keyword}' 검색 결과 내 주요 핵심 키워드 출현 빈도 TOP 20",
        template="plotly_white",
        color="count",
        color_continuous_scale="Viridis",
        text="count"
    )
    fig.update_traces(textposition="outside", textfont_size=13)
    fig.update_layout(
        title_font=dict(size=20),
        xaxis=dict(title=dict(font=dict(size=15)), tickfont=dict(size=13)),
        yaxis=dict(title=dict(font=dict(size=15)), tickfont=dict(size=13)),
        margin=dict(l=40, r=30, t=70, b=30),
        coloraxis_showscale=False,
        height=chart_height
    )
    return fig


def create_word_cloud_scatter_chart(word_df: pd.DataFrame, selected_keyword: str, chart_height: int = 560) -> go.Figure:
    """
    언급량/빈도수에 비례하여 글자 크기가 달라지는 워드클라우드형 시각화 차트 (TOP 20)
    - 빈도수가 많을수록 큰 글씨(최대 38px)와 큰 원 마커
    - 빈도수가 적을수록 작은 글씨(최소 15px)
    - 2D 분산 배치를 통해 글자가 서로 겹치지 않고 한눈에 직관적으로 조망
    """
    import numpy as np
    subset = word_df[word_df["keyword"] == selected_keyword].sort_values("count", ascending=False).head(20).copy()
    if subset.empty:
        fig = go.Figure()
        fig.update_layout(title="표시할 키워드 데이터가 없습니다.", height=chart_height)
        return fig

    # 빈도수 정규화 (15px ~ 38px 폰트 크기 매핑)
    counts = subset["count"].values
    min_c, max_c = counts.min(), counts.max()
    if max_c > min_c:
        font_sizes = 15 + (counts - min_c) / (max_c - min_c) * 23
        marker_sizes = 30 + (counts - min_c) / (max_c - min_c) * 45
    else:
        font_sizes = np.full(len(counts), 24)
        marker_sizes = np.full(len(counts), 45)

    # 20개 단어를 나선형/원형(Spiral)으로 아름답게 분산 배치
    n = len(subset)
    angles = np.linspace(0, 4 * np.pi, n)
    radii = np.linspace(0.8, 4.0, n)
    x_coords = radii * np.cos(angles)
    y_coords = radii * np.sin(angles)

    fig = go.Figure()

    # 호버 정보와 텍스트를 담은 Scatter Trace (어두운 배경에 최적화된 고대비 네온 컬러)
    fig.add_trace(go.Scatter(
        x=x_coords,
        y=y_coords,
        mode="markers+text",
        text=subset["word"],
        textposition="middle center",
        textfont=dict(
            size=font_sizes,
            color="#ffffff",
            family="Apple SD Gothic Neo, Pretendard, sans-serif"
        ),
        marker=dict(
            size=marker_sizes,
            color=counts,
            colorscale=[
                [0.0, "#0284c7"],    # Sky Blue
                [0.35, "#06b6d4"],   # Cyan
                [0.65, "#10b981"],   # Emerald
                [0.85, "#f59e0b"],   # Amber
                [1.0, "#ef4444"]     # Coral Red
            ],
            showscale=True,
            colorbar=dict(
                title=dict(text="출현 빈도수", font=dict(size=14, color="#f1f5f9")),
                tickfont=dict(size=12, color="#cbd5e1"),
                len=0.8,
                thickness=18
            ),
            opacity=0.92,
            line=dict(width=2, color="#38bdf8")
        ),
        hovertemplate="<b>%{text}</b><br>언급/출현 빈도: <b>%{marker.color:,}회</b><extra></extra>"
    ))

    fig.update_layout(
        title=dict(
            text=f"☁️ '{selected_keyword}' 관련 연관어 가중치 워드클라우드 (TOP 20 다크 모드)",
            font=dict(size=22, color="#f8fafc", family="Apple SD Gothic Neo, sans-serif")
        ),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False),
        paper_bgcolor="#0b0f19",
        plot_bgcolor="#0f172a",
        height=chart_height,
        margin=dict(l=30, r=30, t=70, b=30),
        hoverlabel=dict(
            bgcolor="#1e293b",
            bordercolor="#38bdf8",
            font_size=15,
            font_color="#ffffff"
        )
    )
    return fig


# -------------------------------------------------------------
# 카테고리별 심층 EDA 차트 5종 (파이 차트 전면 배제)
# -------------------------------------------------------------

def create_category_source_bar_chart(df: pd.DataFrame, cat_name: str, chart_height: int = 500) -> go.Figure:
    """[EDA 차트 1] 주요 출처/언론사/작성자 TOP 10 가로 막대 차트"""
    if df.empty or "source" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="출처 데이터가 없습니다.", height=chart_height)
        return fig

    source_counts = df["source"].value_counts().head(10).sort_values(ascending=True)
    fig = px.bar(
        x=source_counts.values,
        y=source_counts.index,
        orientation="h",
        labels={"x": "수집 게시물 수", "y": "출처 / 작성자"},
        title=f"📊 [차트 1] {cat_name} 주요 출처/작성자 TOP 10 분포",
        template="plotly_white",
        color=source_counts.values,
        color_continuous_scale="Teal",
        text=source_counts.values
    )
    fig.update_traces(textposition="outside", textfont_size=13)
    fig.update_layout(
        title_font=dict(size=18),
        xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12)),
        yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=13)),
        margin=dict(l=20, r=30, t=60, b=30),
        coloraxis_showscale=False,
        height=chart_height
    )
    return fig


def create_category_text_length_hist(df: pd.DataFrame, cat_name: str, chart_height: int = 500) -> go.Figure:
    """[EDA 차트 2] 본문 요약 글자수 분포 히스토그램"""
    if df.empty or "desc_len" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="텍스트 길이 데이터가 없습니다.", height=chart_height)
        return fig

    fig = px.histogram(
        df,
        x="desc_len",
        color="keyword" if "keyword" in df.columns and df["keyword"].nunique() > 1 else None,
        nbins=25,
        marginal="box",
        labels={"desc_len": "본문 요약 글자수 (자)", "count": "게시물 수"},
        title=f"📏 [차트 2] {cat_name} 본문 요약 텍스트 길이 분포 및 상단 박스플롯",
        template="plotly_white",
        color_discrete_sequence=PALETTE
    )
    fig.update_layout(
        title_font=dict(size=18),
        xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12)),
        yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12), showgrid=True, gridcolor="#f3f4f6"),
        margin=dict(l=30, r=20, t=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
        height=chart_height
    )
    return fig


def create_category_length_boxplot(df: pd.DataFrame, cat_name: str, chart_height: int = 500) -> go.Figure:
    """[EDA 차트 3] 키워드별 제목 vs 본문 길이 사분위 및 이상치 박스플롯"""
    if df.empty or "title_len" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="박스플롯용 데이터가 없습니다.", height=chart_height)
        return fig

    has_kw = "keyword" in df.columns and df["keyword"].nunique() > 0
    fig = px.box(
        df,
        x="keyword" if has_kw else None,
        y="title_len",
        color="keyword" if has_kw else None,
        points="all",
        labels={"title_len": "제목 글자수 (자)", "keyword": "검색어"},
        title=f"📦 [차트 3] {cat_name} 검색어별 제목 글자수 사분위 분포 및 이상치",
        template="plotly_white",
        color_discrete_sequence=PALETTE
    )
    fig.update_layout(
        title_font=dict(size=18),
        xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=13)),
        yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12), showgrid=True, gridcolor="#f3f4f6"),
        margin=dict(l=30, r=20, t=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
        height=chart_height
    )
    return fig


def create_category_weekday_bar_chart(df: pd.DataFrame, cat_name: str, chart_height: int = 500) -> go.Figure:
    """[EDA 차트 4] 요일별 게시물 등록 분포 막대 차트"""
    if df.empty or "weekday" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="요일 데이터가 없습니다.", height=chart_height)
        return fig

    weekday_order = ["월", "화", "수", "목", "금", "토", "일"]
    df_valid = df[df["weekday"].isin(weekday_order)]
    if df_valid.empty:
        fig = go.Figure()
        fig.update_layout(title="유효한 날짜/요일 정보가 없습니다.", height=chart_height)
        return fig

    day_counts = df_valid.groupby(["weekday", "keyword" if "keyword" in df_valid.columns else "weekday"]).size().reset_index(name="count")
    fig = px.bar(
        day_counts,
        x="weekday",
        y="count",
        color="keyword" if "keyword" in df_valid.columns and df_valid["keyword"].nunique() > 1 else None,
        category_orders={"weekday": weekday_order},
        barmode="group",
        text_auto=True,
        labels={"weekday": "발행 요일", "count": "게시물 수", "keyword": "검색어"},
        title=f"📅 [차트 4] {cat_name} 요일별 발행/등록 분포 비교",
        template="plotly_white",
        color_discrete_sequence=PALETTE
    )
    fig.update_traces(textposition="outside", textfont_size=13)
    fig.update_layout(
        title_font=dict(size=18),
        xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=13)),
        yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12), showgrid=True, gridcolor="#f3f4f6"),
        margin=dict(l=30, r=20, t=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
        height=chart_height
    )
    return fig


def create_category_date_timeline_chart(df: pd.DataFrame, cat_name: str, chart_height: int = 500) -> go.Figure:
    """[EDA 차트 5] 날짜별 게시물 수집 추이 시계열 막대/라인 차트"""
    if df.empty or "pub_date" not in df.columns:
        fig = go.Figure()
        fig.update_layout(title="발행일 데이터가 없습니다.", height=chart_height)
        return fig

    df_dated = df[df["pub_date"] != ""].copy()
    if df_dated.empty:
        fig = go.Figure()
        fig.update_layout(title="분석 가능한 날짜 정보가 없습니다.", height=chart_height)
        return fig

    timeline_df = df_dated.groupby(["pub_date", "keyword"]).size().reset_index(name="count").sort_values("pub_date")
    fig = px.line(
        timeline_df,
        x="pub_date",
        y="count",
        color="keyword",
        markers=True,
        labels={"pub_date": "발행 날짜", "count": "발행 건수", "keyword": "검색어"},
        title=f"🕒 [차트 5] {cat_name} 일자별 게시물 수집 빈도 추이",
        template="plotly_white",
        color_discrete_sequence=PALETTE
    )
    fig.update_traces(line=dict(width=3), marker=dict(size=7))
    fig.update_layout(
        title_font=dict(size=18),
        xaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12)),
        yaxis=dict(title=dict(font=dict(size=14)), tickfont=dict(size=12), showgrid=True, gridcolor="#f3f4f6"),
        margin=dict(l=30, r=20, t=60, b=30),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, font=dict(size=13)),
        height=chart_height
    )
    return fig

