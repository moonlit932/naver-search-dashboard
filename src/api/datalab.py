from typing import Dict, Any, List
from .client import NaverApiClient

class NaverDatalabService:
    """
    네이버 데이터랩 검색어 트렌드 API 서비스
    엔드포인트: POST /v1/datalab/search
    """

    ENDPOINT = "/search-trend/v1/search"

    def __init__(self, client: NaverApiClient):
        self.client = client

    def get_search_trend(
        self,
        start_date: str,       # YYYY-MM-DD
        end_date: str,         # YYYY-MM-DD
        time_unit: str,        # date, week, month
        keywords_groups: List[Dict[str, Any]], # [{"groupName": "아이폰", "keywords": ["아이폰", "iphone"]}]
        device: str = "",      # pc, mo, or 빈문자열(전체)
        gender: str = "",      # m, f, or 빈문자열(전체)
        ages: List[str] = None # ["1", "2", ...]
    ) -> Dict[str, Any]:
        """
        데이터랩 검색어 트렌드 API 호출
        """
        body = {
            "startDate": start_date,
            "endDate": end_date,
            "timeUnit": time_unit,
            "keywordGroups": keywords_groups
        }
        if device:
            body["device"] = device
        if gender:
            body["gender"] = gender
        if ages:
            body["ages"] = ages

        return self.client.post(self.ENDPOINT, body)
