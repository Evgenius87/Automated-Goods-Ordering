import uuid

from fastapi import HTTPException,APIRouter, Depends, status, UploadFile, File, Form
from sqlalchemy.orm import Session

from src.schemas import DishResponseModel, UpdateDishModel, DishModel
from src.database.db_connection import get_db
from src.repository import dishes
from src.services.images import image_cloudinary, resize_image
from src.services.roles import access_A, access_ABC, access_ABCU



router = APIRouter(prefix='/dishes', tags=["Dishes"])

@router.get('/{dish_id}', response_model=DishResponseModel,
            dependencies=[Depends(access_ABCU)])
async def get_dish(dish_id:int, db: Session = Depends(get_db)):
     dish =  await dishes.get_dish(dish_id, db)
     if dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found"
        )
     return dish


@router.get('/', 
            dependencies=[Depends(access_ABCU)],
            response_model=list[DishResponseModel], 
            status_code=status.HTTP_200_OK)
async def get_all_dishes(db: Session = Depends(get_db)):
     dishes_list = await dishes.get_all_dishes(db)
     if dishes_list is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dishes not found"
        )
     return dishes_list

     
@router.post('/create_new_dish',
             dependencies=[Depends(access_ABC)],
             response_model=DishResponseModel, 
             status_code=status.HTTP_201_CREATED,
             )
async def create_new_dish(body: DishModel,
                          db: Session = Depends(get_db)):
    dish = await dishes.add_new_dish(body, db)
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found"
        )
    return dish


@router.patch('/update_photo',
              dependencies=[Depends(access_ABC)],
              response_model=DishResponseModel, 
              status_code=status.HTTP_202_ACCEPTED)
async def update_photo(id: int = Form(), 
                       file: UploadFile = File(), 
                       db: Session=Depends(get_db)):
    file.filename = f"{uuid.uuid4()}.jpg"
    contents =  await file.read()
    resized_contents = resize_image(contents)
    image_url, image_public_id = await image_cloudinary.add_image(resized_contents)
    dish = await dishes.update_photo(id, image_url, image_public_id, db)
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found"
        )
    return dish


@router.patch("/patch", 
              dependencies=[Depends(access_ABC)],
              response_model=DishResponseModel,
              status_code=status.HTTP_202_ACCEPTED)
async def patch_dish(body: UpdateDishModel, db: Session = Depends(get_db)):
    dish = await dishes.patch(body, db)
    if dish is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Dish not found"
        )
    return dish


@router.delete("/delete/{id}", 
               dependencies=[Depends(access_A)],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_dish(id: int, db: Session = Depends(get_db)):
    return await dishes.delete_dish(id, db)
