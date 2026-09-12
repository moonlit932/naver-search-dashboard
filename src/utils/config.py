import os
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

def get_naver_credentials(client_id_override: str = None, client_secret_override: str = None):
    """
    환경변수 또는 UI에서 오버라이드된 Client ID/Secret을 반환합니다.
    """
    load_dotenv(override=True)
    client_id = client_id_override or os.getenv("NAVER_CLIENT_ID", "").strip()
    client_secret = client_secret_override or os.getenv("NAVER_CLIENT_SECRET", "").strip()
    return client_id, client_secret
