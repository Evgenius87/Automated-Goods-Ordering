import uuid
import io

from fastapi import HTTPException,APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from PIL import Image

from src.schemas import IngredientUpdateModel, IngredientResponseModel, OrederIngByProvider
from src.database.db_connection import get_db
from src.database.models import Dish, Category
from src.repository import dishes, ingredients
from src.services.images import image_cloudinary, resize_image


router = APIRouter(prefix='/ingredients', tags=["Ingredients"])



@router.get("/", response_model=list[IngredientResponseModel])
async def get_all_ingredients(db: Session = Depends(get_db)):
    ingredients_list = await ingredients.get_all_ingredients(db)
    if ingredients_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredients not found"
        )
    return ingredients_list


@router.get("/orders", response_model=list[OrederIngByProvider])
async def get_orders(db: Session = Depends(get_db)):
    order_list = await ingredients.get_order(db)
    if not order_list:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Order not found"
        )
    return order_list


@router.get("/{ingredient_id}", response_model=IngredientResponseModel)
async def get_ingredient(ingredient_id: int, db: Session = Depends(get_db)):
    ingredient = await ingredients.get_ingredient(ingredient_id, db)
    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found"
        )
    return ingredient


@router.get("/create_ingredients/{num}", response_model=list[IngredientResponseModel])
async def create_ingregients(num: int, db: Session=Depends(get_db)):
    print("routs/create_ingredients")
    new_ingredients = await ingredients.create_ingredients(db)
    if new_ingredients is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredients not found"
        )
    return new_ingredients


@router.post("/send_orders")
async def send_orders(body: list[OrederIngByProvider], 
                      db: Session = Depends(get_db)):
    return await ingredients.send_order_to_provider(body, db)


@router.patch("/patch", response_model=IngredientResponseModel)
async def patch_ingredient(body: IngredientUpdateModel, 
                           db: Session = Depends(get_db)):
    ingredient = await ingredients.patch_ingredient(body, db)
    if ingredient is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Ingredient not found"
        )
    return ingredient


@router.delete("/delete_all")
async def delete_ingredients(db: Session=Depends(get_db)):
    return await ingredients.delete_all(db)