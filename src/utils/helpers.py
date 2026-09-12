import re
import html
from typing import List, Dict, Any

def clean_html(raw_html: str) -> str:
    """HTML 태그 및 특수문자 엔티티(&quot;, &lt; 등)를 정제합니다."""
    if not raw_html:
        return ""
    # HTML 엔티티 언이스케이프
    text = html.unescape(raw_html)
    # 태그 제거
    cleanr = re.compile('<.*?>')
    clean_text = re.sub(cleanr, '', text)
    # 불필요한 연속 공백 정제
    return ' '.join(clean_text.split())

def extract_keywords_frequency(texts: List[str], top_n: int = 25) -> List[Dict[str, Any]]:
    """고도화된 한국어 불용어 처리 기반 단어 빈도 분석 (뉴스/블로그/카페 특화)"""
    stopwords = {
        # 기본 문법 및 형식 불용어
        '이', '그', '저', '것', '수', '등', '및', '을', '를', '에', '에서', '으로', '로',
        '의', '가', '은', '는', '과', '와', '도', '고', '하다', '있다', '되다', '대한',
        '통해', '위해', '관련', '더', '잘', '추천', '방법', '이용', '정보', '사진',
        '후기', '후', '전', '오늘', '내일', '곳', '때', '중', '더보기', '모두', '또한',
        '때문', '경우', '대해', '다시', '다른', '하나', '모든', '가장', '매우', '진짜',
        # 네이버 및 플랫폼 특화 불용어
        '네이버', '검색', '블로그', '포스팅', '카페', '글', '작성', '작성자', '조회',
        '댓글', '스크랩', '공유', '이웃', '서로이웃', '소통', '방문', '일기', '리뷰',
        # 뉴스 및 기사 특화 불용어
        '기자', '뉴스', '보도', '속보', '종합', '기사', '사진', '영상', '출처', '제공',
        '무단', '전재', '배포', '금지', '저작권자', '구독', '언론사', '앵커', '리포트',
        '취재', '연합뉴스', '뉴시스', '뉴스1', 'kbs', 'mbc', 'sbs', 'ytn', 'jtbc',
        # 일반 포털/웹문서 불용어
        '바로가기', '홈페이지', '사이트', '다운로드', '클릭', '확인', '안내', '문의',
        '페이지', '더보기', '메뉴', '카테고리', '내용', '본문', '링크', '게시판'
    }
    
    word_counts = {}
    for text in texts:
        cleaned = clean_html(text)
        # 한글 및 영문 2글자 이상 단어 추출
        words = re.findall(r'[가-힣a-zA-Z]{2,}', cleaned)
        for w in words:
            w_lower = w.lower()
            if w_lower in stopwords:
                continue
            # 한 글자 또는 너무 긴 이상 문자열 배제
            if len(w_lower) < 2 or len(w_lower) > 15:
                continue
            word_counts[w_lower] = word_counts.get(w_lower, 0) + 1
            
    sorted_words = sorted(word_counts.items(), key=lambda x: x[1], reverse=True)[:top_n]
    return [{"word": word, "count": count} for word, count in sorted_words]
