from fastapi import HTTPException,APIRouter, Depends, status
from sqlalchemy.orm import Session


from src.schemas import TagResponseModel
from src.database.db_connection import get_db
from src.repository import tags
from src.services.roles import access_A, access_ABC, access_ABCU



router = APIRouter(prefix='/tags', tags=["Tags"])

@router.get("/", 
            dependencies=[Depends(access_ABCU)],
            response_model=list[TagResponseModel], 
            status_code=status.HTTP_200_OK)
async def get_tags(db: Session = Depends(get_db)):
    tags_list = await tags.get_tags(db)
    if not tags_list:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                            detail="Tags not found")
    return tags_list


@router.delete("/delete/{id}", 
               dependencies=[Depends(access_A)],
               status_code=status.HTTP_204_NO_CONTENT)
async def delete_tag(id: int, db: Session = Depends(get_db)):
    return await tags.delete_tag(id, db)


# @router.delete("/delete_all", status_code=status.HTTP_204_NO_CONTENT)
# async def delete_tags(db: Session = Depends(get_db)):
#     return tags.delete_tags(db)

