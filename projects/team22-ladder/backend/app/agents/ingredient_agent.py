import json
import os

import google.generativeai as genai

from dotenv import load_dotenv

load_dotenv()

genai.configure(
    api_key=os.getenv("GEMINI_API_KEY")
)

model = genai.GenerativeModel(
    "gemini-2.5-flash"
)


def ingredient_agent(state):

    image_path = state["image_path"]

    with open(image_path, "rb") as f:
        image_bytes = f.read()

    response = model.generate_content(
        [
            """
            냉장고 내부 사진입니다.

            보이는 재료만 추출하세요.

            반드시 아래 형식으로만 답하세요.

            {
                "ingredients":[
                    "계란",
                    "우유",
                    "양파"
                ]
            }
            """,
            {
                "mime_type": "image/jpeg",
                "data": image_bytes,
            },
        ]
    )

    text = response.text.strip()

    if text.startswith("```json"):
        text = text.replace("```json", "")
        text = text.replace("```", "")
        text = text.strip()

    data = json.loads(text)

    return {
        "ingredients": data["ingredients"]
    }