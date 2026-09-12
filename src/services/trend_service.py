from typing import Dict, Any, List
import pandas as pd

class TrendService:
    """데이터랩 시계열 데이터를 분석용 DataFrame으로 가공"""

    @staticmethod
    def parse_datalab_response(response_data: Dict[str, Any]) -> pd.DataFrame:
        """
        데이터랩 API 응답을 Date x Keyword DataFrame으로 변환
        결과 형태:
        date | 키워드1 | 키워드2 | ...
        """
        results = response_data.get("results", [])
        if not results:
            return pd.DataFrame()

        dfs = []
        for r in results:
            title = r.get("title", "")
            data_points = r.get("data", [])
            if not data_points:
                continue
            
            df = pd.DataFrame(data_points)
            # data_points: [{'period': '2026-08-01', 'ratio': 23.4}, ...]
            df = df.rename(columns={"period": "date", "ratio": title})
            df["date"] = pd.to_datetime(df["date"])
            df.set_index("date", inplace=True)
            dfs.append(df)

        if not dfs:
            return pd.DataFrame()

        # 여러 키워드 그룹 결합
        merged_df = pd.concat(dfs, axis=1).fillna(0)
        return merged_df.reset_index()
