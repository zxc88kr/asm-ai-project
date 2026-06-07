import json
import os

import google.generativeai as genai

from dotenv import load_dotenv

from app.logger import get_logger

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)

logger = get_logger("fusion_agent")


def fusion_agent(state):

    global_result = state.get("global_ingredients", [])
    window_result = state.get("window_ingredients", [])

    logger.info("결과 통합 시작")
    logger.info(f"global_agent 결과: {len(global_result)}개, window_agent 결과: {len(window_result)}개")

    logger.info("Gemini 2.5-flash API 호출 (중복 제거 및 정제)")
    response = model.generate_content(
        f"""
        Global Agent 결과

        {global_result}

        Window Agent 결과

        {window_result}

        다음은 냉장고 이미지 분석 결과이다.
        
        규칙

        1. 브랜드 제거
        2. 포장 설명 제거
        3. 상품명 제거
        4. 요리에 사용되는 실제 식재료만 남겨라
        5. 한국어로 변환
        6. 중복 제거
        7. 불명확한 항목 제거

        예시

        McCormick Minced Garlic
        → 다진마늘

        Olive Oil
        → 올리브유

        Packaged leafy greens
        → 채소

        Raw meat or poultry
        → 육류

        출력

        {{
            "ingredients":[]
        }}
        """
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        data = json.loads(text)
    except Exception:
        logger.error(f"JSON 파싱 실패, 원본 응답: {text}")
        return {
            "final_ingredients": []
        }

    final = data["ingredients"]
    logger.info(f"최종 재료 목록 확정: {len(final)}개 → {final}")

    return {
        "final_ingredients": final
    }