from fastapi import HTTPException,APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.schemas import PreOrderModel, PreOrderResponse, PreOrderUpdate
from src.database.models import PreOrder, PreOrder_M2M_Dish, Dish



async def get_preorders(db: Session):
    pre_orders = db.query(PreOrder).all()
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


async def update_pre_order(body: PreOrderUpdate, db: Session):
    pre_order = db.query(PreOrder).filter(PreOrder.id == body.id).first()
    if pre_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Not correct id")
    if body.date:
        pre_order.date = body.date
    if body.time:
        pre_order.time = body.time
    if body.name:
        pre_order.name = body.name
    if body.phone:
        pre_order.phone = body.phone
    if body.table:
        pre_order.table = body.table
    if body.guest_counter:
        pre_order.guest_counter = body.guest_counter
    if body.description:
        pre_order.description = body.description
    if body.price:
        pre_order.price = body.price
    if body.discount:
        pre_order.discount = body.discount

    if body.order_dishes:
        order_m2m_dishes = db.query(PreOrder_M2M_Dish).filter(PreOrder_M2M_Dish.pre_order_id == body.id).all()
        for o_m2m_d in order_m2m_dishes:
            db.delete(o_m2m_d)
        for order_detail in body.order_dishes:
            dish = db.query(Dish).filter(Dish.id == order_detail.id)
            if not dish:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Dish with ID {order_detail.id} not found")
            preorder_m2m_dish = PreOrder_M2M_Dish(
                pre_order_id = pre_order.id,
                dish_id = dish.id,
                quantity = o_m2m_d.quantity
            )
            db.add(preorder_m2m_dish)
    db.commit()
    db.refresh(pre_order)
    return pre_order



async def delete_pre_order(id: int, db: Session):
    pre_order = db.query(PreOrder).filter(PreOrder.id == id).first()
    if not pre_order:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Pre-order not found")
    order_m2m_dishes = db.query(PreOrder_M2M_Dish).filter(PreOrder_M2M_Dish.pre_order_id == id).all()
    db.delete(pre_order)
    for o_m2m_d in order_m2m_dishes:
        db.delete(o_m2m_d)
    db.commit()
    return {"message": "Pre-order was successfull remove"}




