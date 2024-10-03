from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from src.schemas import PremixModel, PremixResponseModel, UpdatePremixModel
from src.database.models import Ingredient, Premix, Premix_M2M_Ingredient, Premix_M2M_Premix, Dish_M2M_Premixes
from src.services.handler_errors import handle_errors


async def get_all_premixes(db: Session) -> list[Premix]:
    premixes = db.query(Premix).all()   
    db.commit()
    return premixes



async def get_premix(id: int, db: Session) -> PremixResponseModel:
    premix = db.query(Premix).filter(Premix.id == id).first()
    return premix



@handle_errors
async def create_premix(body: PremixModel, db: Session):
    new_premix = Premix(name=body.name, description=body.description)
    db.add(new_premix)
    db.commit()
    db.refresh(new_premix)

    for ingredient_detail in body.ingredients:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_detail.id).first()
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient with ID {ingredient_detail.id} not found")
        
        premix_ingredient = Premix_M2M_Ingredient(
            premix_id=new_premix.id,
            ingredient_id=ingredient.id,
            quantity=ingredient_detail.quantity
        )
        db.add(premix_ingredient)
    if body.child_premixes:
        for child_premix_detail in body.child_premixes:
            new_child_premix = db.query(Premix).filter(Premix.id == child_premix_detail.id).first()
            if not new_child_premix:
                raise HTTPException(status_code=404, detail=f"Ingredient with ID {child_premix_detail.id} not found")
            parent_child_premix = Premix_M2M_Premix(
                    parent_premix_id = new_premix.id,
                    child_premix_id = new_child_premix.id,
                    quantity = child_premix_detail.quantity
            )
            db.add(parent_child_premix)
    db.commit()
    db.refresh(new_premix)
    return new_premix



@handle_errors
async def delete_premix(prem_id: int, db: Session):
    premix = db.query(Premix).filter(Premix.id == prem_id).first()
    if not premix:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Premis not found")
    prem_m2m_ing = db.query(Premix_M2M_Ingredient).filter(Premix_M2M_Ingredient.premix_id == prem_id).all()
    prem_m2m_prem = db.query(Premix_M2M_Premix).filter(Premix_M2M_Premix.parent_premix_id == prem_id).all()
    cild_prem_m2m_prem = db.query(Premix_M2M_Premix).filter(Premix_M2M_Premix.child_premix_id == prem_id).all()
    dish_m2m_prem = db.query(Dish_M2M_Premixes).filter(Dish_M2M_Premixes.premix_id == prem_id).all()
    db.delete(premix)
    if prem_m2m_prem:
        for prem_obj in prem_m2m_prem:
            db.delete(prem_obj)
    if prem_m2m_ing:
        for ing_obj in prem_m2m_ing:
            db.delete(ing_obj)
    if cild_prem_m2m_prem:
        for ch_prem_obj in cild_prem_m2m_prem:
            db.delete(ch_prem_obj)
    if dish_m2m_prem:
        for dish_obj in dish_m2m_prem:
            db.delete(dish_obj)
    db.commit()
    return {"message": "Premix successfuly deleted"}


@handle_errors
async def update_premix(body: UpdatePremixModel, db: Session):

    premix = db.query(Premix).filter(Premix.id == body.id).first()
    if body.name:
        premix.name = body.name
    if body.description:
        premix.description = body.description
    if body.ingredients:
        prem_m2m_ingred = db.query(Premix_M2M_Ingredient).filter(Premix_M2M_Ingredient.premix_id == body.id).all()
        
        for p_m2m_i in prem_m2m_ingred:
            db.delete(p_m2m_i)
        for ingredient_detail in body.ingredients:
            ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_detail.id).first()
            if not ingredient:
                raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                                    detail=f"Ingredient with ID {ingredient_detail.id} not found")
            dish_ingredient = Premix_M2M_Ingredient(
                premix_id = premix.id,
                ingredient_id = ingredient.id,
                quantity = ingredient_detail.quantity
            )
            db.add(dish_ingredient)
    if body.child_premixes:

        prem_m2m_prem = db.query(Premix_M2M_Premix).filter(Premix_M2M_Premix.parent_premix_id == body.id).all()
        for p_m2m_p in prem_m2m_prem:
            db.delete(p_m2m_p)
        for child_premix_detail in body.child_premixes:
            new_child_premix = db.query(Premix).filter(Premix.id == child_premix_detail.id).first()
            if not new_child_premix:
                raise HTTPException(status_code=404, detail=f"Ingredient with ID {child_premix_detail.id} not found")
            parent_child_premix = Premix_M2M_Premix(
                    parent_premix_id = premix.id,
                    child_premix_id = new_child_premix.id,
                    quantity = child_premix_detail.quantity
            )
            db.add(parent_child_premix)
    db.commit()
    db.refresh(premix)
    return premix
        