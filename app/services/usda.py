from typing import List
import httpx
from app.config import settings
from app.schemas import FoodItem
from app.models import FoodSource

BASE_URL = "https://api.nal.usda.gov/fdc/v1"

NUTRIENT_IDS = {
    "energy": 1008,
    "protein": 1003,
    "carbs": 1005,
    "fat": 1004,
}


async def search(query: str, limit: int = 5) -> List[FoodItem]:
    if not settings.USDA_API_KEY:
        return []

    async with httpx.AsyncClient(timeout=10.0) as client:
        response = await client.get(
            f"{BASE_URL}/foods/search",
            params={
                "api_key": settings.USDA_API_KEY,
                "query": query,
                "pageSize": limit,
            },
        )
        response.raise_for_status()
        data = response.json()

        return [_parse_food(food) for food in data.get("foods", [])]


def _parse_food(food: dict) -> FoodItem:
    nutrients = {}
    for n in food.get("foodNutrients", []):
        nutrient_id = n.get("nutrientId")
        if nutrient_id:
            nutrients[nutrient_id] = n.get("value", 0)

    return FoodItem(
        name=food.get("description", "Unknown"),
        calories=nutrients.get(NUTRIENT_IDS["energy"], 0),
        protein_g=nutrients.get(NUTRIENT_IDS["protein"]),
        carbs_g=nutrients.get(NUTRIENT_IDS["carbs"]),
        fat_g=nutrients.get(NUTRIENT_IDS["fat"]),
        source=FoodSource.USDA,
    )
