from fastapi import FastAPI, HTTPException
from fastapi import UploadFile
from fastapi import File
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from pydantic import BaseModel, Field

from app.recipe_agent import RecipeGenerationError, generate_recipes

load_dotenv()

import tempfile

from app.graph.ingredient_graph import graph

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

    temp = tempfile.NamedTemporaryFile(
        delete=False,
        suffix=".jpg"
    )

    temp.write(
        await file.read()
    )

    result = graph.invoke(
        {
            "image_path": temp.name,
            "ingredients": []
        }
    )

    return result


class RecipeGenerateRequest(BaseModel):
    ingredients: list[str] = Field(default_factory=list)
    required_ingredients: list[str] = Field(default_factory=list)
    expiring_ingredients: list[str] = Field(default_factory=list)
    sauces: list[str] = Field(default_factory=list)
    tools: list[str] = Field(default_factory=list)
    extra_ingredients: list[str] = Field(default_factory=list)


@app.post("/recipes/generate")
def recipes_generate(request: RecipeGenerateRequest):
    try:
        recipes = generate_recipes(request.model_dump())
    except RecipeGenerationError as exc:
        message = str(exc)
        if "재료가 없습니다" in message:
            raise HTTPException(status_code=400, detail=message) from exc
        raise HTTPException(status_code=503, detail=message) from exc
    except Exception as exc:
        raise HTTPException(status_code=503, detail=f"레시피 생성 중 오류가 발생했습니다: {exc}") from exc

    return recipes