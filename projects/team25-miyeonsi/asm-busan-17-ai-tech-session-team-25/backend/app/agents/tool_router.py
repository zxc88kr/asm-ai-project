from app.services.airscraper_client import AirScraperClient

_NO_DESTINATION_MSG = "어디로 가고 싶은지 알려줘! 목적지가 있어야 항공편을 찾을 수 있어."
_NO_RESULTS_MSG = "항공편을 찾을 수 없어. 날짜나 도시를 바꿔서 다시 시도해볼까?"


class ToolRouter:
    def __init__(self):
        self._flight_client = AirScraperClient()

    def route(self, intent: str, params: dict) -> dict:
        """
        intent_classifier의 결과를 받아 적절한 도구를 호출하고 결과를 반환.

        Args:
            intent: classifier가 반환한 intent 문자열 ("tool" 일 때만 의미 있음)
            params: classifier가 추출한 파라미터 dict

        Returns:
            {
                "tool_name": str,
                "results": list[dict],
                "summary": str   # dialogue_generator가 참고할 한 줄 요약
            }
        """
        if intent != "tool":
            return {"tool_name": "none", "results": [], "summary": ""}

        destination = params.get("destination")
        if not destination:
            return {
                "tool_name": "flight_search",
                "results": [],
                "summary": _NO_DESTINATION_MSG,
            }

        origin = params.get("origin", "ICN")
        date = params.get("date") or _default_date()
        adults = int(params.get("adults") or 1)

        results = self._flight_client.search_flights(origin, destination, date, adults)

        if not results:
            return {
                "tool_name": "flight_search",
                "results": [],
                "summary": _NO_RESULTS_MSG,
            }

        summary = _build_summary(origin, destination, date, results)
        return {
            "tool_name": "flight_search",
            "results": results,
            "summary": summary,
        }


def _default_date() -> str:
    from datetime import date, timedelta
    return (date.today() + timedelta(days=30)).isoformat()


def _build_summary(origin: str, destination: str, date: str, results: list[dict]) -> str:
    cheapest = min(results, key=lambda r: r.get("price_krw", 0))
    return (
        f"{origin}→{destination} {date} 기준 항공편 {len(results)}개 검색 완료. "
        f"최저가: {cheapest['airline']} {cheapest['flight_number']} "
        f"{cheapest['price_krw']:,}원 ({cheapest['departure'][11:16]} 출발)"
    )
