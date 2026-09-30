import asyncio
from fastapi import APIRouter, Query, HTTPException
from app.schemas import FoodSearchResponse, FoodItem
from app.services import open_food_facts, usda

router = APIRouter(prefix="/foods", tags=["Food Search"])


@router.get("/search", response_model=FoodSearchResponse)
async def search_foods(q: str = Query(..., min_length=1, description="Search query")):
    off_task = open_food_facts.search(q, limit=5)
    usda_task = usda.search(q, limit=5)

    results_tuple = await asyncio.gather(off_task, usda_task, return_exceptions=True)

    results = []
    for r in results_tuple:
        if isinstance(r, list):
            results.extend(r)

    return FoodSearchResponse(
        query=q,
        results=results,
        total_results=len(results),
    )


@router.get("/barcode/{code}", response_model=FoodItem)
async def lookup_barcode(code: str):
    result = await open_food_facts.get_product_by_barcode(code)
    if not result:
        raise HTTPException(status_code=404, detail="Product not found")
    return result
