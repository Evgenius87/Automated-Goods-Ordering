from fastapi import HTTPException,APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.schemas import PreOrderModel, PreOrderResponse, PreOrderUpdate
from src.database.db_connection import get_db
from src.repository import preorders as repository_preorders
from src.services.images import image_cloudinary, resize_image
from src.services.roles import access_A, access_ABC, access_ABCU



router = APIRouter(prefix='/preorders', tags=["Pre-Orders"])



@router.get("/", response_model=PreOrderResponse,
            dependencies= Depends(access_ABCU),
            status_code=status.HTTP_200_OK)
async def get_preorders(db: Session = Depends(get_db)):
    pre_orders = await repository_preorders.get_preorders(db)
    if pre_orders is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pre-orsers not found")
    return pre_orders


@router.post("/create", response_model=PreOrderResponse,
             dependencies= Depends(access_ABCU),
             status_code=status.HTTP_201_CREATED)
async def create_preorder(body: PreOrderModel, db: Session = Depends(get_db)):
    pre_order = await repository_preorders.create_preorders(body, db)
    if pre_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pre-orser not found")
    return pre_order


@router.patch("/patch", response_model=PreOrderResponse,
              dependencies=Depends(access_ABCU),
              status_code=status.HTTP_202_ACCEPTED)
async def patch_pre_order(body: PreOrderUpdate, db: Session=Depends(get_db)):
    updated_pre_order = await repository_preorders.update_pre_order(body, db)
    if updated_pre_order is None:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Pre-orser not found")
    return updated_pre_order


@router.delete("/delete/{id}", dependencies=Depends(access_A),
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_pre_order(id: int, db: Session=Depends(get_db)):
    return await repository_preorders.delete_pre_order(id, db)



