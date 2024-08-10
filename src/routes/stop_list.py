from fastapi import HTTPException,APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session
from PIL import Image

from src.schemas import StopListModel
from src.database.db_connection import get_db
from src.database.models import Dish, Category
from src.repository import stop_list as sl
from src.services.images import image_cloudinary, resize_image
from src.services.roles import access_ABC, access_A, access_ABCU


router = APIRouter(prefix='/stop-list', tags=["Stop-list"])


@router.get("/", 
            dependencies=[Depends(access_ABCU)],
            response_model=StopListModel, 
            status_code=status.HTTP_200_OK)
async def get_stop_list(db: Session = Depends(get_db)):
    stop_list = await sl.get_stop_list(db)
    if not stop_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Stop-List is empty")
    return stop_list


@router.get("/update", 
            dependencies=[Depends(access_ABC)],
            response_model=StopListModel, 
            status_code=status.HTTP_200_OK)
async def update_stop_list(db: Session = Depends(get_db)):
    stop_list = await sl.update_stop_list(db)
    if not stop_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Stop-List is empty")
    return stop_list

