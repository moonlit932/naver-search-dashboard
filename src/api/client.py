import requests
from typing import Dict, Any, Optional

class NaverApiClient:
    """네이버 오픈 API 공통 HTTP 클라이언트 (NAVER API HUB 및 Developers API 지원)"""

    BASE_URL = "https://naverapihub.apigw.ntruss.com"

    def __init__(self, client_id: str, client_secret: str):
        self.client_id = client_id.strip() if client_id else ""
        self.client_secret = client_secret.strip() if client_secret else ""

    def is_configured(self) -> bool:
        return bool(self.client_id and self.client_secret)

    def _get_headers(self) -> Dict[str, str]:
        # NAVER API HUB (x-ncp-apigw-api-key-id / x-ncp-apigw-api-key)
        # 및 구 Developers 호환 헤더 동시 전송
        return {
            "x-ncp-apigw-api-key-id": self.client_id,
            "x-ncp-apigw-api-key": self.client_secret,
            "X-Naver-Client-Id": self.client_id,
            "X-Naver-Client-Secret": self.client_secret,
            "Content-Type": "application/json"
        }

    def get(self, endpoint: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """GET 요청 실행"""
        if not self.is_configured():
            raise ValueError("네이버 API 인증 정보(Client ID 및 Secret)가 설정되지 않았습니다.")
            
        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()
        del headers["Content-Type"]  # GET 요청 시 제외

        response = requests.get(url, headers=headers, params=params, timeout=10)
        
        if response.status_code != 200:
            error_msg = response.text
            try:
                err_json = response.json()
                error_msg = err_json.get("errorMessage", err_json.get("message", response.text))
            except Exception:
                pass
            raise RuntimeError(f"Naver API Error [{response.status_code}]: {error_msg}")

        return response.json()

    def post(self, endpoint: str, body: Dict[str, Any]) -> Dict[str, Any]:
        """POST 요청 실행 (데이터랩 등)"""
        if not self.is_configured():
            raise ValueError("네이버 API 인증 정보(Client ID 및 Secret)가 설정되지 않았습니다.")

        url = f"{self.BASE_URL}{endpoint}"
        headers = self._get_headers()

        response = requests.post(url, headers=headers, json=body, timeout=10)

        if response.status_code != 200:
            error_msg = response.text
            try:
                err_json = response.json()
                error_msg = err_json.get("errorMessage", err_json.get("message", response.text))
            except Exception:
                pass
            raise RuntimeError(f"Naver API Error [{response.status_code}]: {error_msg}")

        return response.json()
