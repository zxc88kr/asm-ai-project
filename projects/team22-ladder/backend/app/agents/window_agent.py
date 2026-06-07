import io
import json
import os

from PIL import Image

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

logger = get_logger("window_agent")


def crop_image(
    image_path,
    overlap_ratio=0.3
):
    image = Image.open(image_path)

    width, height = image.size

    cols = 2
    rows = 2

    base_w = width // cols
    base_h = height // rows

    overlap_w = int(base_w * overlap_ratio)
    overlap_h = int(base_h * overlap_ratio)

    crops = []

    for r in range(rows):
        for c in range(cols):

            left = c * base_w - overlap_w // 2
            top = r * base_h - overlap_h // 2

            right = (c + 1) * base_w + overlap_w // 2
            bottom = (r + 1) * base_h + overlap_h // 2

            left = max(0, left)
            top = max(0, top)

            right = min(width, right)
            bottom = min(height, bottom)

            crop = image.crop(
                (
                    left,
                    top,
                    right,
                    bottom
                )
            )

            crops.append(crop)

    return crops


def window_agent(state):

    image_path = state["image_path"]

    logger.info("이미지 분할 분석 시작")
    logger.info("이미지를 2×2 격자로 크롭 (오버랩 30%)")

    crops = crop_image(
        image_path
    )

    contents = [
        """
        당신은 냉장고 재료 분석 전문가이다.

        아래 이미지는 같은 냉장고를
        4개의 영역으로 나눈 사진들이다.

        목표:
        모든 이미지를 종합하여
        요리에 사용할 수 있는 식재료를 추출하라.

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

        
        """
    ]

    for idx, crop in enumerate(crops):


        buffer = io.BytesIO()

        crop.save(
            buffer,
            format="JPEG"
        )

        contents.append(
            {
                "mime_type": "image/jpeg",
                "data": buffer.getvalue()
            }
        )


    logger.info("Gemini 2.5-flash API 호출 (4개 크롭 이미지)")
    response = model.generate_content(
        contents
    )

    text = response.text.strip()

    if text.startswith("```"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    try:
        data = json.loads(text)
        ingredients = data.get("ingredients", [])
    except Exception:
        ingredients = []

    logger.info(f"응답 수신 완료 → 재료 {len(ingredients)}개 추출: {ingredients}")

    return {
        "window_ingredients": ingredients
    }