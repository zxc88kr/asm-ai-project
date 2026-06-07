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

logger = get_logger("global_agent")


def global_agent(state):

    image_path = state["image_path"]

    logger.info("냉장고 전체 이미지 분석 시작")

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    logger.info("Gemini 2.5-flash API 호출 (전체 이미지)")
    response = model.generate_content(
        [
            """
            당신은 냉장고 재료 분석 전문가이다.

            냉장고 전체 사진을 보고
            보이는 식재료를 추출하라.

            규칙:
            - 가능한 구체적으로
            - 영어 금지
            - 브랜드명 금지
            - 식재료만 출력
            - JSON만 출력

            좋은 예시:
            계란
            식빵
            양파
            버터
            시금치

            나쁜 예시:
            Packaged leafy greens
            Raw meat
            McCormick Garlic
            
            출력 형식:
            배열만 출력 금지
            설명 금지
            Markdown 금지
            반드시 아래 형식만 출력

            {
                "ingredients":[]
            }

            """,
            {
                "mime_type": "image/jpeg",
                "data": image_bytes
            }
        ]
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    data = json.loads(text)
    ingredients = data["ingredients"]

    logger.info(f"응답 수신 완료 → 재료 {len(ingredients)}개 추출: {ingredients}")

    return {
        "global_ingredients": ingredients
    }