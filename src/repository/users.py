import os
from random import randint

from dotenv import load_dotenv
from fastapi import status, HTTPException
from sqlalchemy.orm import Session

from src.schemas import UserResponseModel, UserModel, UserRegistrationBase, GoogleAuthResp
from src.database.models import  User, Token

from src.repository.tags import find_tags



async def get_user(id: int, db: Session):
    
    return db.query(User).filter(User.id == id).first()


async def get_users(db: Session):

    return db.query(User).all()


async def patch_user(body: UserResponseModel, db: Session):

    user = db.query(User).filter(User.id == body.id).first()

    if body.first_name:
        user.first_name = body.first_name
    if body.last_name:
        user.last_name = body.last_name
    if body.email:
        user.email = body.email
    if body.information:
        user.information = body.information
    if body.forward_provider_message:
        user.forward_provider_message = body.forward_provider_message

    db.commit()

    return user


async def delete_user(id: int, db: Session):

    user = db.query(User).filter(User.id == id).first()
    db.delete(user)
    db.commit()

    return {"message": "OK"}


async def create_user(body: UserRegistrationBase, db: Session, bot_auth_code: str):

    from src.services.auth import auth_service
    
    users = db.query(User).all()
    hash_password = auth_service.get_password_hash(body.password)
    hash_code = auth_service.get_password_hash(bot_auth_code)
    user = User(
        first_name = body.first_name,
        last_name = body.last_name,
        email = body.email,
        password = hash_password,
        secret_code = hash_code
    )

    if not users:
        user.role = 'admin'

    db.add(user)
    db.commit()
    response_user = db.query(User).order_by(User.id.desc()).first()

    return user

async def create_user_by_google_cred(data: GoogleAuthResp, db: Session, bot_auth_code: str):
    from src.services.auth import auth_service
    
    users = db.query(User).all()
    hash_code = auth_service.get_password_hash(bot_auth_code)
    user = User(
        first_name = data.given_name,
        last_name = data.family_name,
        email = data.email,
        secret_code = hash_code
    )

    if not users:
        user.role = 'admin'

    db.add(user)
    db.commit()

    return user


async def get_user_by_email(email: str, db: Session):

    user = db.query(User).filter(User.email == email).first()

    return user


async def update_token(user: User, refresh_token: str, db: Session):

    user.refresh_token = refresh_token
    db.commit()
    db.refresh(user)

    return user


async def add_token_to_blacklist(token: str, db: Session):
    
    token = Token(access_token=token)
    db.add(token)
    db.commit()

    return True