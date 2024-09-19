from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from src.schemas import StopListModel, DishResponseModel
from src.database.models import Dish
from src.services.images import image_cloudinary
from src.repository.tags import find_tags
from src.repository import dishes as reepository_dishes
from src.repository import ingredients as repository_ingredients
from src.services.handler_errors import handle_errors



@handle_errors
async def get_stop_list(db: Session) -> StopListModel:
    stop_list_dishes = db.query(Dish).filter(Dish.stop_list == True).all()
    running_out_dishes = db.query(Dish).filter(Dish.runing_out == True).all()
    need_to_sold_dishes = db.query(Dish).filter(Dish.need_to_sold == True).all()

    check_list = StopListModel(
        stop_list=stop_list_dishes,
        runing_out=running_out_dishes,
        need_to_sold=need_to_sold_dishes
    )
    return check_list

@handle_errors
async def update_stop_list(db: Session):
    await reepository_dishes.update_stop_list(db)
    # await repository_ingredients.update_ingerdients(db)
    return await get_stop_list(db)