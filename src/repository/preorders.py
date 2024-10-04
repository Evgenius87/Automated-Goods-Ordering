from fastapi import HTTPException,APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.schemas import PreOrderModel, PreOrderResponse
from src.database.models import PreOrder, PreOrder_M2M_Dish, Dish



async def get_preorders(db: Session):
    pre_orders = db.query(get_preorders).all()
    return pre_orders


async def create_preorders(body: PreOrderModel, db: Session):
    new_pre_order = PreOrder(
        date = body.date,
        time = body.time,
        name = body.name,
        phone = body.phone,
        table = body.table,
        guest_counter = body.guest_counter,
        description = body.description,
        price = body.price,
        discount = body.discount
    )
    db.add(new_pre_order)
    db.commit()
    db.refresh(new_pre_order)
    if body.order_dishes:
        for dish_details in body.order_dishes:
            dish = db.query(Dish).filter(Dish.id == dish_details.id).first()
            if not dish:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Dish whis id {dish_details.id} not found")
            preorder_dish = PreOrder_M2M_Dish(
                pre_order_id = new_pre_order.id,
                dish_id = dish_details.id,
                quantity = dish_details.quantity
                    )
            db.add(preorder_dish)
    db.commit()
    db.refresh(new_pre_order)
    return new_pre_order


