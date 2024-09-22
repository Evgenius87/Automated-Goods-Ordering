from fastapi import HTTPException,APIRouter, Depends, status
from fastapi.security import HTTPBearer
from sqlalchemy.orm import Session
from PIL import Image

from src.schemas import CommentResponeModel, CommentModel, CommentUpdateModel
from src.database.db_connection import get_db
from src.database.models import User
from src.repository import comments as repository_comments
from src.services.roles import access_A, access_ABC, access_ABCU
from src.services.auth import auth_service





router = APIRouter(prefix='/comments', tags=["Comments"])

security = HTTPBearer()


@router.get('/{dish_id}', response_model=list[CommentResponeModel])
async def get_comments(dish_id: int,
                       db: Session = Depends(get_db),
                       current_user = Depends(auth_service.get_current_user)):
    comments = await repository_comments.get_comments(dish_id, db, current_user)
    if comments is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found"
        )
    return comments


@router.post('/create', response_model=CommentResponeModel, status_code=status.HTTP_201_CREATED)
async def create_comment(body: CommentModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.create_comment(body, current_user, db)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found")
    return comment


@router.patch('/update', response_model=CommentResponeModel)
async def update_comment(body: CommentUpdateModel, db: Session = Depends(get_db),
                         current_user: User = Depends(auth_service.get_current_user)):
    comment = await repository_comments.update_comment(body, db, current_user)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Comments not found")
    return comment


@router.delete('/del/{comment_id}')# dependencies=[Depends(access_AM)])
async def remove_comment(comment_id: int, 
                         db: Session = Depends(get_db),
                         current_user = Depends(auth_service.get_current_user)):
    comment = await repository_comments.remove_comment(comment_id, db, current_user)
    if not comment:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No such comment")
    return comment