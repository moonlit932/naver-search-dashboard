from typing import Dict, Any, List
from .client import NaverApiClient

class NaverSearchService:
    """
    네이버 검색 API 8개 카테고리 수집 서비스
    1. news (뉴스)
    2. blog (블로그)
    3. webkr (웹문서)
    4. image (이미지)
    5. kin (지식iN)
    6. local (지역)
    7. cafearticle (카페글)
    8. encyc (백과사전)
    """

    CATEGORIES = {
        "news": {"name": "뉴스", "endpoint": "/search/v1/news"},
        "blog": {"name": "블로그", "endpoint": "/search/v1/blog"},
        "webkr": {"name": "웹문서", "endpoint": "/search/v1/webkr"},
        "image": {"name": "이미지", "endpoint": "/search/v1/image"},
        "kin": {"name": "지식iN", "endpoint": "/search/v1/kin"},
        "local": {"name": "지역", "endpoint": "/search/v1/local"},
        "cafearticle": {"name": "카페글", "endpoint": "/search/v1/cafearticle"},
        "encyc": {"name": "백과사전", "endpoint": "/search/v1/encyc"}
    }

    def __init__(self, client: NaverApiClient):
        self.client = client

    def search_category(
        self,
        category: str,
        query: str,
        display: int = 30,
        start: int = 1,
        sort: str = "sim"
    ) -> Dict[str, Any]:
        """특정 카테고리에 대한 검색 결과 조회"""
        if category not in self.CATEGORIES:
            raise ValueError(f"지원하지 않는 카테고리입니다: {category}")

        endpoint = self.CATEGORIES[category]["endpoint"]
        params = {
            "query": query,
            "display": min(display, 100),
            "start": start,
            "sort": sort
        }
        # 백과사전 및 웹문서는 sort 파라미터가 없거나 다를 수 있으므로 예외 처리
        if category in ["webkr", "encyc", "image"]:
            if "sort" in params and category != "image":
                del params["sort"]

        return self.client.get(endpoint, params)

    def search_all_categories(
        self,
        query: str,
        display: int = 100,
        sort: str = "sim"
    ) -> Dict[str, Dict[str, Any]]:
        """
        8개 카테고리 전체 조회 및 요약 정보 반환 (페이지네이션 지원: 최대 200건 수집)
        - 100건 이하: 단일 호출 (display=N, start=1)
        - 101~200건: 2회 분할 호출 (1차: display=100, start=1 / 2차: display=N-100, start=101)
        """
        results = {}
        for cat_key, cat_info in self.CATEGORIES.items():
            try:
                collected_items = []
                total_reported = 0

                if display <= 100:
                    res = self.search_category(cat_key, query, display=display, start=1, sort=sort)
                    total_reported = res.get("total", 0)
                    collected_items = res.get("items", [])
                else:
                    # 1차 수집 (최대 100건)
                    res1 = self.search_category(cat_key, query, display=100, start=1, sort=sort)
                    total_reported = res1.get("total", 0)
                    collected_items.extend(res1.get("items", []))

                    # 2차 수집 (추가 필요 건수: 101번부터)
                    needed_extra = min(display - 100, 100)
                    if total_reported > 100 and needed_extra > 0:
                        try:
                            res2 = self.search_category(cat_key, query, display=needed_extra, start=101, sort=sort)
                            collected_items.extend(res2.get("items", []))
                        except Exception:
                            # 일부 카테고리(백과/웹문서 등)의 페이지네이션 제한 시 1차 결과 유지
                            pass

                results[cat_key] = {
                    "name": cat_info["name"],
                    "total": total_reported,
                    "items": collected_items,
                    "success": True,
                    "error": None
                }
            except Exception as e:
                results[cat_key] = {
                    "name": cat_info["name"],
                    "total": 0,
                    "items": [],
                    "success": False,
                    "error": str(e)
                }
        return results
