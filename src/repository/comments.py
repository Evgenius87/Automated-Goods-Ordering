from sqlalchemy.orm import Session
from sqlalchemy import and_

from src.schemas import CommentModel, CommentResponseModel
from src.database.models import User, Comment



async def get_comments(dish_id: int, db: Session, user: User):
    return db.query(Comment).filter(and_(Comment.user_id == user.id, Comment.dish_id == dish_id)). all()



async def create_comment(body: CommentModel, user: User, db: Session):
    comment = Comment(
        comment = body.comment,
        user_id = user.id,
        dish_id = body.dish_id
    )
    db.add(comment)
    db.commit()
    return comment


async def update_comment(body: CommentResponseModel, db: Session, current_user: User):
    comment = db.query(Comment).filter(Comment.id == body.id).first()
    comment.comment = body.comment
    db.commit()
    db.refresh()
    return comment


async def remove_comment(comment_id: int, db: Session, user: User):
    comment = db.query(Comment).filter(and_(Comment.id == comment_id, Comment.user_id == user.id)).first()
    if comment:
        db.delete(comment)
        db.commit()
    return comment