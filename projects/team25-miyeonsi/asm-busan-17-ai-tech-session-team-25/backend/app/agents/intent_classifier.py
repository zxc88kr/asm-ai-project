import os
import json
from datetime import date
from openai import OpenAI


def _build_system_prompt() -> str:
    """현재 날짜를 주입한 의도 분류 시스템 프롬프트 생성.

    날짜는 LLM이 연도를 추론하지 않고 month/day/year만 추출한다.
    실제 연도 보정(오늘 이전이면 내년, 이후면 올해)은 파이썬(_resolve_date)이 결정론적으로 처리한다.
    """
    today = date.today()
    return f"""당신은 여행 메이트 게임의 의도 분류기입니다.
사용자의 발화를 분석하여 아래 세 가지 의도 중 하나로 분류하고, JSON 형식으로만 응답하세요.

오늘 날짜는 {today.isoformat()}입니다.

의도 유형:
- "dialogue": 일반 대화 (인사, 감정 표현, 잡담 등)
- "tool": 항공편 검색이 필요한 발화 (출발지/목적지/날짜 언급 또는 항공편 문의)
- "selection": 제시된 선택지에 대한 응답 (번호 선택, "첫 번째", "그걸로" 등)

tool 의도 시 params에서 IATA 코드로 공항을 추출하세요.
주요 공항 IATA: 인천=ICN, 김포=GMP, 부산=PUS, 도쿄(나리타)=NRT, 도쿄(하네다)=HND, 오사카=KIX, 파리=CDG, 런던=LHR, 방콕=BKK, 뉴욕=JFK, 싱가포르=SIN

날짜 추출 규칙 (중요):
- 날짜는 직접 계산하지 말고, 사용자가 말한 그대로 month(1-12), day(1-31), year를 추출만 하세요.
- 사용자가 연도를 말하지 않았으면 year는 반드시 null로 두세요. (연도를 스스로 추측하지 마세요)
- 날짜를 전혀 언급하지 않으면 month, day, year 모두 null로 두세요.
- 연도 보정은 시스템이 자동으로 처리합니다.

응답 형식 (JSON only):
{{
  "intent": "dialogue" | "tool" | "selection",
  "params": {{
    // tool인 경우: {{"origin": "ICN", "destination": "NRT", "month": 8, "day": 1, "year": null, "adults": 1}}
    // selection인 경우: {{"selected_option": "선택한 내용"}}
    // dialogue인 경우: {{}}
  }},
  "reason": "분류 이유 한 줄"
}}

예시:
사용자: "안녕! 오늘 날씨 어때?"
→ {{"intent": "dialogue", "params": {{}}, "reason": "일반 인사말"}}

사용자: "서울에서 도쿄 가는 비행기 찾아줘"
→ {{"intent": "tool", "params": {{"origin": "ICN", "destination": "NRT", "month": null, "day": null, "year": null, "adults": 1}}, "reason": "항공편 검색 요청(날짜 미언급)"}}

사용자: "8월 15일에 인천에서 파리 가고 싶어"
→ {{"intent": "tool", "params": {{"origin": "ICN", "destination": "CDG", "month": 8, "day": 15, "year": null, "adults": 1}}, "reason": "월/일만 명시(연도 미지정)"}}

사용자: "2026년 12월 25일 인천에서 런던"
→ {{"intent": "tool", "params": {{"origin": "ICN", "destination": "LHR", "month": 12, "day": 25, "year": 2026, "adults": 1}}, "reason": "연도까지 명시"}}

사용자: "2번으로 할게"
→ {{"intent": "selection", "params": {{"selected_option": "2번"}}, "reason": "선택지 응답"}}"""


def _resolve_date(month, day, year) -> str | None:
    """월/일/연도로부터 ISO 날짜 문자열 생성.

    - 연도가 주어지면 그대로 사용.
    - 연도 미지정 시: 올해 날짜가 오늘 이전이면 내년, 오늘 이후(당일 포함)면 올해.
    - 월/일이 없거나 유효하지 않으면 None.
    """
    if not month or not day:
        return None
    try:
        m, d = int(month), int(day)
        today = date.today()
        if year:
            return date(int(year), m, d).isoformat()
        candidate = date(today.year, m, d)
        if candidate < today:
            candidate = date(today.year + 1, m, d)
        return candidate.isoformat()
    except (ValueError, TypeError):
        return None


class IntentClassifier:
    def __init__(self):
        self._client = OpenAI(
            api_key=os.getenv("UPSTAGE_API_KEY"),
            base_url="https://api.upstage.ai/v1",
        )

    def classify(self, user_message: str, current_chapter: int, current_affinity: int) -> dict:
        """
        Returns:
            {
                "intent": "dialogue" | "tool" | "selection",
                "params": dict,
                "reason": str
            }
        """
        user_context = (
            f"현재 챕터: {current_chapter}, 현재 호감도: {current_affinity}\n"
            f"사용자 발화: {user_message}"
        )

        try:
            response = self._client.chat.completions.create(
                model="solar-pro",
                messages=[
                    {"role": "system", "content": _build_system_prompt()},
                    {"role": "user", "content": user_context},
                ],
                response_format={"type": "json_object"},
                temperature=0.0,
                max_tokens=256,
            )
            result = json.loads(response.choices[0].message.content)
            return self._validate(result)
        except Exception:
            return {"intent": "dialogue", "params": {}, "reason": "분류 실패 - 기본값 반환"}

    def _validate(self, result: dict) -> dict:
        intent = result.get("intent", "dialogue")
        if intent not in ("dialogue", "tool", "selection"):
            intent = "dialogue"

        params = result.get("params", {})
        if intent == "tool":
            # LLM이 추출한 month/day/year를 파이썬에서 결정론적으로 날짜로 보정
            resolved_date = _resolve_date(
                params.pop("month", None),
                params.pop("day", None),
                params.pop("year", None),
            )
            params.setdefault("origin", "ICN")
            params.setdefault("destination", None)
            params["date"] = resolved_date
            params.setdefault("adults", 1)

        return {
            "intent": intent,
            "params": params,
            "reason": result.get("reason", ""),
        }
