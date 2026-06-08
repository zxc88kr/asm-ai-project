import os
import requests
from typing import Optional

# RapidAPI Sky-Scrapper (Air Scraper) 항공권 검색 클라이언트.
# Amadeus 대체용. IATA 코드 -> skyId/entityId 조회 후 항공편 검색.
DEFAULT_HOST = "sky-scrapper.p.rapidapi.com"
SEARCH_AIRPORT_PATH = "/api/v1/flights/searchAirport"
SEARCH_FLIGHTS_PATH = "/api/v1/flights/searchFlights"


class AirScraperClient:
    _place_cache: dict = {}   # IATA -> {"skyId":..., "entityId":...}
    _flight_cache: dict = {}  # "ICN-NRT-2026-08-01-1" -> list[dict]

    def __init__(self):
        self.api_key = os.getenv("RAPIDAPI_KEY", "")
        self.host = os.getenv("RAPIDAPI_FLIGHT_HOST", DEFAULT_HOST)

    @property
    def _headers(self) -> dict:
        return {"x-rapidapi-key": self.api_key, "x-rapidapi-host": self.host}

    def _resolve_place(self, iata: str) -> Optional[dict]:
        """IATA 코드를 Sky-Scrapper의 skyId/entityId로 변환 (캐싱)."""
        iata = iata.upper()
        if iata in AirScraperClient._place_cache:
            return AirScraperClient._place_cache[iata]
        try:
            resp = requests.get(
                f"https://{self.host}{SEARCH_AIRPORT_PATH}",
                headers=self._headers,
                params={"query": iata, "locale": "en-US"},
                timeout=15,
            )
            resp.raise_for_status()
            data = resp.json().get("data", [])
            picked = None
            for item in data:
                params = item.get("navigation", {}).get("relevantFlightParams", {})
                if params.get("skyId") == iata:
                    picked = params
                    break
            if not picked and data:
                picked = data[0].get("navigation", {}).get("relevantFlightParams")
            if picked and picked.get("skyId") and picked.get("entityId"):
                place = {"skyId": picked["skyId"], "entityId": picked["entityId"]}
                AirScraperClient._place_cache[iata] = place
                return place
            return None
        except Exception:
            return None

    def search_flights(self, origin: str, destination: str, date: str, adults: int = 1) -> list[dict]:
        cache_key = f"{origin}-{destination}-{date}-{adults}"
        if cache_key in AirScraperClient._flight_cache:
            return AirScraperClient._flight_cache[cache_key]

        if not self.api_key:
            return self._fallback_data(origin, destination, date)

        origin_place = self._resolve_place(origin)
        dest_place = self._resolve_place(destination)
        if not origin_place or not dest_place:
            return self._fallback_data(origin, destination, date)

        try:
            resp = requests.get(
                f"https://{self.host}{SEARCH_FLIGHTS_PATH}",
                headers=self._headers,
                params={
                    "originSkyId": origin_place["skyId"],
                    "destinationSkyId": dest_place["skyId"],
                    "originEntityId": origin_place["entityId"],
                    "destinationEntityId": dest_place["entityId"],
                    "date": date,
                    "cabinClass": "economy",
                    "adults": adults,
                    "sortBy": "best",
                    "currency": "KRW",
                    "market": "ko-KR",
                    "countryCode": "KR",
                },
                timeout=40,
            )
            resp.raise_for_status()
            itineraries = resp.json().get("data", {}).get("itineraries", [])
            results = self._parse_itineraries(itineraries)
            if not results:
                return self._fallback_data(origin, destination, date)
            AirScraperClient._flight_cache[cache_key] = results
            return results
        except Exception:
            return self._fallback_data(origin, destination, date)

    def _parse_itineraries(self, itineraries: list) -> list[dict]:
        results = []
        for itin in itineraries[:3]:
            try:
                leg = itin["legs"][0]
                price_raw = itin.get("price", {}).get("raw")
                carrier = leg.get("carriers", {}).get("marketing", [{}])[0]
                segment = (leg.get("segments") or [{}])[0]
                code = segment.get("marketingCarrier", {}).get("displayCode", "") \
                    or carrier.get("alternateId", "")
                results.append({
                    "airline": carrier.get("name", "Unknown"),
                    "flight_number": f"{code}{segment.get('flightNumber', '')}".strip(),
                    "departure": leg.get("departure", ""),
                    "arrival": leg.get("arrival", ""),
                    "price_krw": int(price_raw) if price_raw is not None else 0,
                    "duration": _format_duration(leg.get("durationInMinutes")),
                    "stops": leg.get("stopCount", 0),
                })
            except (KeyError, ValueError, IndexError, TypeError):
                continue
        return results

    def _fallback_data(self, origin: str, destination: str, date: str) -> list[dict]:
        return [
            {
                "airline": "Korean Air",
                "flight_number": "KE001",
                "departure": f"{date}T09:00:00",
                "arrival": f"{date}T11:30:00",
                "price_krw": 320000,
                "duration": "2시간 30분",
                "stops": 0,
            },
            {
                "airline": "Asiana Airlines",
                "flight_number": "OZ201",
                "departure": f"{date}T14:00:00",
                "arrival": f"{date}T16:40:00",
                "price_krw": 285000,
                "duration": "2시간 40분",
                "stops": 0,
            },
            {
                "airline": "Jeju Air",
                "flight_number": "7C101",
                "departure": f"{date}T18:30:00",
                "arrival": f"{date}T21:00:00",
                "price_krw": 198000,
                "duration": "2시간 30분",
                "stops": 0,
            },
        ]


def _format_duration(minutes: Optional[int]) -> str:
    if not minutes:
        return ""
    return f"{minutes // 60}시간 {minutes % 60}분"
