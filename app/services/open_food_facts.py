from typing import Optional, List
import httpx
from app.schemas import FoodItem
from app.models import FoodSource

BASE_URL = "https://world.openfoodfacts.org"
SEARCH_URL = "https://search.openfoodfacts.org"
HEADERS = {"User-Agent": "CalorieTrackerAPI/1.0 (github.com/calorie-tracker)"}


async def get_product_by_barcode(barcode: str) -> Optional[FoodItem]:
    async with httpx.AsyncClient(timeout=30.0) as client:
        response = await client.get(
            f"{BASE_URL}/api/v2/product/{barcode}",
            headers=HEADERS,
            params={"fields": "product_name,nutriments"},
        )
        if response.status_code == 404:
            return None
        response.raise_for_status()
        data = response.json()

        if data.get("status") != 1:
            return None

        return _parse_product(data["product"])


async def search(query: str, limit: int = 5) -> List[FoodItem]:
    async with httpx.AsyncClient(timeout=15.0) as client:
        response = await client.get(
            f"{SEARCH_URL}/search",
            headers=HEADERS,
            params={
                "q": query,
                "page_size": limit,
            },
        )
        response.raise_for_status()
        data = response.json()

        results = []
        for product in data.get("hits", []):
            if product.get("product_name"):
                results.append(_parse_product(product))
        return results


def _parse_product(product: dict) -> FoodItem:
    nutriments = product.get("nutriments", {})
    calories = nutriments.get("energy-kcal_100g")
    if calories is None:
        energy_kj = nutriments.get("energy_100g", 0)
        calories = energy_kj / 4.184

    return FoodItem(
        name=product.get("product_name", "Unknown"),
        calories=round(calories, 1),
        protein_g=nutriments.get("proteins_100g"),
        carbs_g=nutriments.get("carbohydrates_100g"),
        fat_g=nutriments.get("fat_100g"),
        source=FoodSource.OPEN_FOOD_FACTS,
    )
