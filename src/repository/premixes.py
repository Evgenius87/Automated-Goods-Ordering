from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from src.schemas import PremixModel, PremixResponseModel, UpdatePremixModel
from src.database.models import Ingredient, Premix, Premix_M2M_Ingredient
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
    # Створення нового премікса
    new_premix = Premix(name=body.name, description=body.description)
    db.add(new_premix)
    db.commit()
    db.refresh(new_premix)

    # Додавання інгредієнтів і кількостей до премікса
    for ingredient_detail in body.ingredients:
        ingredient = db.query(Ingredient).filter(Ingredient.id == ingredient_detail.id).first()
        if not ingredient:
            raise HTTPException(status_code=404, detail=f"Ingredient with ID {ingredient_detail.id} not found")
        
        # Створення m2m зв'язку з кількістю
        premix_ingredient = Premix_M2M_Ingredient(
            premix_id=new_premix.id,
            ingredient_id=ingredient.id,
            quantity=ingredient_detail.quantity
        )
        db.add(premix_ingredient)
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
    db.delete(premix)
    for obj in prem_m2m_ing:
        db.delete(obj)
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

    db.commit()
    db.refresh(premix)
    return premix
        