from fastapi import HTTPException,APIRouter, Depends, status
from sqlalchemy.orm import Session

from src.schemas import IngredientUpdateModel, IngredientResponseModel, OrederIngByProvider
from src.database.db_connection import get_db
from src.repository import ingredients
from src.services.roles import access_A, access_ABC, access_ABCU


router = APIRouter(prefix='/ingredients', tags=["Ingredients"])



@router.get("/", 
            dependencies=[Depends(access_ABCU)],
            response_model=list[IngredientResponseModel])
async def get_all_ingredients(db: Session = Depends(get_db)):
    ingredients_list = await ingredients.get_all_ingredients(db)
    if ingredients_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredients not found"
        )
    return ingredients_list


@router.get("/orders", 
            dependencies=[Depends(access_ABC)],
            response_model=list[OrederIngByProvider])
async def get_orders(db: Session = Depends(get_db)):
    order_list = await ingredients.get_order(db)
    if not order_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order_list


@router.get("/{ingredient_id}", 
            dependencies=[Depends(access_ABC)],
            response_model=IngredientResponseModel)
async def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = await ingredients.get_ingredient(ingredient_id, db)
    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found"
        )
    return ingredient


# @router.get("/create_ingredients/{num}", 
#             dependencies=[Depends(access_ABC)],
#             response_model=list[IngredientResponseModel])
# async def create_ingregients(num: int, db: Session=Depends(get_db)):
#     print("routs/create_ingredients")
#     new_ingredients = await ingredients.create_ingredients(db)
#     if new_ingredients is None:
#         raise HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND, detail="Ingredients not found"
#         )
#     return new_ingredients


@router.post("/send_orders",
             dependencies=[Depends(access_ABC)],)
async def send_orders(body: list[OrederIngByProvider], 
                      db: Session = Depends(get_db)):
    return await ingredients.send_order_to_provider(body, db)


@router.patch("/patch", 
              dependencies=[Depends(access_ABC)],
              response_model=IngredientResponseModel)
async def patch_ingredient(body: IngredientUpdateModel, 
                           db: Session = Depends(get_db)):
    ingredient = await ingredients.patch_ingredient(body, db)
    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found"
        )
    return ingredient


# @router.delete("/delete_all")
# async def delete_ingredients(db: Session=Depends(get_db)):
#     return await ingredients.delete_all(db)