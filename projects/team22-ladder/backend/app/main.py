from fastapi import FastAPI, HTTPException
from fastapi import UploadFile
from fastapi import File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.recipe_agent import RecipeGenerationError, generate_recipes
from app.logger import get_logger

load_dotenv()

import tempfile

from app.graph.ingredient_graph import graph

logger = get_logger("main")

app = FastAPI(
    title="Ladder API",
    version="0.1.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/health")
def health():
    return {
        "status": "ok"
    }


@app.post("/ingredients/image")
async def ingredient_image(
    file: UploadFile = File(...)
):
    logger.info(f"POST /ingredients/image 요청 수신 (파일명: {file.filename})")

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    )

    temp.write(
        await file.read()
    )
    logger.info(f"임시 파일 저장 완료: {temp.name}")

    logger.info("LangGraph 재료 분석 그래프 시작")
    result = graph.invoke(
        {
            "image_path": temp.name,
            "global_ingredients": [],
            "window_ingredients": [],
            "final_ingredients": []
        }
    )

    final = result["final_ingredients"]
    logger.info(f"그래프 실행 완료 → 최종 재료 {len(final)}개 추출")
    logger.info(f"응답 반환: {final}")

    return {
        "ingredients": final
    }


class RecipeGenerateRequest(BaseModel):
    ingredients: list[str] = Field(default_factory=list)
    required_ingredients: list[str] = Field(default_factory=list)
    expiring_ingredients: list[str] = Field(default_factory=list)
    sauces: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    extra_ingredients: list[str] = Field(default_factory=list)


@app.post("/recipes/generate")
def recipes_generate(request: RecipeGenerateRequest):
    data = request.model_dump()
    logger.info(
        f"POST /recipes/generate 요청 수신 "
        f"(재료 {len(data['ingredients'])}개, "
        f"필수 {len(data['required_ingredients'])}개, "
        f"유통기한임박 {len(data['expiring_ingredients'])}개)"
    )
    try:
        recipes = generate_recipes(data)
    except RecipeGenerationError as exc:
        message = str(exc)
        if "재료가 없습니다" in message:
            raise HTTPException(status_code=400, detail=message) from exc
        raise HTTPException(status_code=503, detail=message) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"레시피 생성 중 오류가 발생했습니다: {exc}") from exc

    top_count = len(recipes.get("top_recipes", []))
    category_count = len([k for k, v in recipes.get("recipes", {}).items() if v])
    logger.info(f"레시피 생성 완료 → top {top_count}개, 카테고리 {category_count}종")

    return recipes
