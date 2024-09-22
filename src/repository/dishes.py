import time
import logging

from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from src.schemas import DishModel, UpdateDishModel, StopListModel
from src.database.models import Dish, Category, Ingredient, Premix, Dish_M2M_Ingredients, Dish_M2M_Premixes
from src.services.images import image_cloudinary
from src.repository.tags import find_tags
from src.repository import ingredients as repository_ing
from src.services.handler_errors import handle_errors


logger = logging.getLogger(__name__)

async def get_all_dishes(db: Session):
    return db.query(Dish).order_by(Dish.id).all()
    


async def get_dish(dish_id: int, db: Session):
    return db.query(Dish).filter(Dish.id == dish_id).first()
  

@handle_errors
async def add_new_dish(body: DishModel, db: Session):
    if body.tags:
        tags = await find_tags(body.tags, db)
    new_dish = Dish(dish_name=body.dish_name, 
                         description=body.description, 
                         tags=tags, 
                         category_id=body.category_id,
                         price=body.price,
                         ended = False,
                         runing_out = False,
                         need_to_sold = False,
                         )
    db.add(new_dish)
    db.commit()
    db.refresh(new_dish)
    if body.ingredients:
        for ingredient_detail in body.ingredients:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_detail.id).first()
            if not ingredient:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Ingredient with ID {ingredient_detail.id} not found")
            dish_ingredient = Dish_M2M_Ingredients(
                dish_id = new_dish.id,
                ingredient_id = ingredient.id,
                quantity = ingredient_detail.quantity
            )
            db.add(dish_ingredient)
    if body.premixes:
        for premix_detail in body.premixes:
            premix = db.query(Premix).filter(Premix.id == premix_detail.id).first()
            if not premix:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Premix with ID {premix_detail.id} not found")
            dish_premix = Dish_M2M_Premixes(
                dish_id = new_dish.id,
                premix_id = premix.id,
                quantity = premix_detail.quantity
            )
            db.add(dish_premix)
    db.commit()
    db.refresh(new_dish)
    return new_dish


@handle_errors
async def update_photo(id: int, image_url: str, image_public_id: str, db: Session):
    dish = db.query(Dish).filter(Dish.id == id).first()
    if dish.image_public_id:
        await image_cloudinary.delete_image(dish.image_public_id)
    dish.image_url = image_url
    dish.image_public_id = image_public_id
    db.commit()
    return dish


@handle_errors
async def patch(body: UpdateDishModel, db: Session):
    dish = db.query(Dish).filter(Dish.id == body.id).first()
    
    if body.dish_name:
        dish.dish_name = body.dish_name
    if body.description:
        dish.description = body.description 
    if body.category:
        category = db.query(Category).filter(Category.name == body.category).first()
        dish.category_id = category.id
    if body.price:
        dish.price = body.price
    if body.tags:
        tags = await find_tags(body.tags, db)
        dish.tags = tags
    if body.ingredients:
        dish_m2m_ingred = db.query(Dish_M2M_Ingredients).filter(Dish_M2M_Ingredients.dish_id == body.id).all()
        for d_m2m_i in dish_m2m_ingred:
            db.delete(d_m2m_i)
        for ingredient_detail in body.ingredients:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_detail.id).first()
            if not ingredient:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Ingredient with ID {ingredient_detail.id} not found")
            dish_ingredient = Dish_M2M_Ingredients(
                dish_id = dish.id,
                ingredient_id = ingredient.id,
                quantity = ingredient_detail.quantity
            )
            db.add(dish_ingredient)
    if body.premixes:
        dish_m2m_prem = db.query(Dish_M2M_Premixes).filter(Dish_M2M_Premixes.dish_id == body.id).all()
        for d_m2m_p in dish_m2m_prem:
            db.delete(d_m2m_p)
        for premix_detail in body.premixes:
            premix = db.query(Premix).filter(Premix.id == premix_detail.id).first()
            if not premix:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Premix with ID {premix_detail.id} not found")
            dish_premix = Dish_M2M_Premixes(
                dish_id = dish.id,
                premix_id = premix.id,
                quantity = premix_detail.quantity
            )
            db.add(dish_premix)
    db.commit()
    db.refresh(dish)
    return dish


@handle_errors
async def delete_dish(dish_id: int, db: Session):
    dish = db.query(Dish).filter(Dish.id == dish_id).first()
    if not dish:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Dish not found")
    d_m2m_i = db.query(Dish_M2M_Ingredients).filter(Dish_M2M_Ingredients.dish_id == dish_id).all()
    d_m2m_p = db.query(Dish_M2M_Premixes).filter(Dish_M2M_Premixes.dish_id == dish_id).all()
    db.delete(dish)
    if d_m2m_i:  
        for obj_1 in d_m2m_i:
            db.delete(obj_1)
    if d_m2m_p:
        for obj_2 in d_m2m_p:
            db.delete(obj_2)
    db.commit()
    return{"message": "The Dish is correctly deleted"}


# @handle_errors
# async def find_ingredients_id_of_dish(dish_id: int, db: Session):
#     time_start = time.time()
#     logging.basicConfig(level=logging.INFO)
#     d_m2m_i_list = db.query(Dish_M2M_Ingredients).filter(Dish_M2M_Ingredients.dish_id == dish_id).all()
#     ingredients_id = [d_m2m_i.ingredient_id for d_m2m_i in d_m2m_i_list]
#     ingredients_id = list(set(ingredients_id))
#     time_end = time.time()
#     logger.info(f"find_ingredients_id_of_dish - {time_end - time_start}")
#     return ingredients_id


# @handle_errors
# async def check_available_ing(ingredients_id: list[int], db: Session):
#     time_start = time.time()
#     logging.basicConfig(level=logging.INFO)
#     need_to_sold = False
#     runing_out = False
#     stop_list = False
#     ingredient = db.query(Ingredient).filter(Ingredient.id.in_(ingredients_id),
#                                              Ingredient.amount < Ingredient.stock_minimum).first()
#     if ingredient:
#         stop_list = True
#         return stop_list, runing_out, need_to_sold
#     ingredient = db.query(Ingredient).filter(Ingredient.id.in_(ingredients_id),
#                                              Ingredient.amount >= Ingredient.stock_minimum,
#                                              Ingredient.amount <= Ingredient.min_acceptable).first()
#     if ingredient:
#         runing_out = True
#         return stop_list, runing_out, need_to_sold
#     ingredient = db.query(Ingredient).filter(Ingredient.id.in_(ingredients_id),
#                                              Ingredient.amount > Ingredient.stock_maximum).first()
#     if ingredient:
#         need_to_sold = True
#         return stop_list, runing_out, need_to_sold
#     time_end = time.time()
#     logger.info(f"check_available_ing - {time_end - time_start}")
#     return stop_list, runing_out, need_to_sold
    

@handle_errors
async def get_updated_stop_list(data: dict, db: Session):

    dishes_data = {}
    for key, value in data.items():
        d_m2m_i_list = db.query(Dish_M2M_Ingredients).filter(Dish_M2M_Ingredients.ingredient_id.in_(value)).all()
        dishes_id = [d_m2m_i.dish_id for d_m2m_i in d_m2m_i_list]
        dishes_data[key] = dishes_id

    need_to_sold = set(dishes_data.get("need_to_sold"))
    running_out = set(dishes_data.get("runing_out"))
    ended = set(dishes_data.get("ended"))

    need_to_sold = need_to_sold - ended - running_out
    running_out = running_out - ended

    need_to_sold = db.query(Dish).filter(Dish.id.in_(list(need_to_sold))).all()
    running_out = db.query(Dish).filter(Dish.id.in_(list(running_out))).all()
    ended = db.query(Dish).filter(Dish.id.in_(list(ended))).all()

    for dish in ended:
        dish.ended = True

    for dish in running_out:
        dish.runing_out = True

    for dish in need_to_sold:
        dish.need_to_sold = True
    
    db.commit()

    stop_list = StopListModel(
        ended=ended,
        runing_out=running_out,
        need_to_sold=need_to_sold
    )

    return stop_list


    



# @handle_errors
# async def update_stop_list(db: Session):
#     stop_list_data = await repository_ing.update_ingerdients(db)
#     return await get_check_list(stop_list_data, db)
#     # dishes = db.query(Dish).all()
#     # for dish in dishes:
#     #     ingredients_id = await find_ingredients_id_of_dish(dish.id, db)
#     #     stop_list, runing_out, need_to_sold = await check_available_ing(ingredients_id, db)
#     #     dish.stop_list = stop_list
#     #     dish.runing_out = runing_out
#     #     dish.need_to_sold = need_to_sold
#     #     db.commit()
#     #     db.refresh(dish)
            

# async def check_dishes_for_stop_list(ingredient: Ingredient, db: Session):
#     need_to_sold = False
#     runing_out = False
#     stop_list = False
#     if ingredient.min_acceptable > ingredient.amount:
#         stop_list = True
#     elif ingredient.min_acceptable < ingredient.amount and ingredient.amount < ingredient.stock_minimum:
#         runing_out = True
#     elif ingredient.amount > ingredient.stock_maximum:
#         need_to_sold = True
#     d_m2m_i_list = db.query(Dish_M2M_Ingredients).filter(Dish_M2M_Ingredients.ingredient_id == ingredient.id).all()
#     dishes_id = [d_m2m_i.dish_id for d_m2m_i in d_m2m_i_list]
#     print(dishes_id)
#     for dish_id in dishes_id:
#         dish = await get_dish(dish_id, db)
#         dish: Dish
#         print(dish.dish_name)
#         print(dish.need_to_sold)
#         dish.need_to_sold = need_to_sold
#         dish.runing_out = runing_out
#         dish.stop_list = stop_list
#         db.commit()
#         db.refresh(dish)
