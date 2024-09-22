from fastapi import HTTPException,APIRouter, Depends, status
from sqlalchemy.orm import Session


from src.schemas import PremixModel,PremixResponseModel, UpdatePremixModel
from src.database.db_connection import get_db
from src.repository import premixes
from src.services.roles import access_A, access_ABC, access_ABCU


router = APIRouter(prefix='/premixes', tags=["Premixes"])



@router.get("/", 
            dependencies=[Depends(access_ABC)],
            response_model=list[PremixResponseModel])
async def get_all_premixes(db: Session = Depends(get_db)):
    premixes_list = await premixes.get_all_premixes(db)
    
    if premixes_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Premixes not found"
        )
    return premixes_list


@router.get("/{premix_id}", 
            dependencies=[Depends(access_ABC)],
            response_model=PremixResponseModel)
async def get_premix(ingredient_id: int, db: Session = Depends(get_db)):
    premix = await premixes.get_premix(ingredient_id, db)
    
    if premix is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Premix not found"
        )
    return premix


@router.post("/create_premix", 
             dependencies=[Depends(access_ABC)],
             response_model=PremixResponseModel)
async def create_premix(body: PremixModel, db: Session = Depends(get_db)):
    premix = await premixes.create_premix(body, db)
    
    if premix is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Premix not found"
        )
    return premix


@router.patch("/update", dependencies=[Depends(access_ABC)],
            response_model=PremixResponseModel,
            status_code=status.HTTP_200_OK)
async def update_premix(body: UpdatePremixModel, db: Session = Depends(get_db)):
    premix = await premixes.update_premix(body, db)
    
    if premix is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Premix not found"
        )
    return premix



@router.delete("/delete/{id}",
               dependencies=[Depends(access_ABC)],)
async def delete_premix(id: int, db: Session = Depends(get_db)):
    return await premixes.delete_premix(id, db)
