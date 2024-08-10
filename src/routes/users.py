from dotenv import load_dotenv


from fastapi import APIRouter, Depends, status, HTTPException, dependencies
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from src.schemas import  OkResponseModel, UserResponseModel, UserModel
from src.database.db_connection import get_db
from src.repository import users as repository_users
from src.database.models import User
from src.schemas import UserModel, UserRegistrationBase, UserUpdateModel
from src.services.auth import auth_service
from src.services.roles import access_A, access_ABC, access_ABCU



router = APIRouter(prefix='/users', tags=["Users"])

security = HTTPBearer()



@router.get("/", response_model=list[UserResponseModel],
            dependencies=[Depends(access_A)],
            status_code=status.HTTP_200_OK)
async def get_users(db: Session = Depends(get_db)):
    users = await repository_users.get_users(db)
    if not users:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="Users not found")
    return users


@router.get("/me", response_model=UserResponseModel,
            dependencies=[Depends(access_ABCU)],
            status_code=status.HTTP_200_OK)
async def get_me(current_user: User = Depends(auth_service.get_current_user)):
    return current_user


@router.get("/user/{id}", response_model=UserResponseModel,
            dependencies=[Depends(access_A)],
            status_code=status.HTTP_200_OK)
async def get_user(id: int, db: Session = Depends(get_db)):
    user = await repository_users.get_user(id, db)
    if not user:
        return HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                             detail="User not found")
    return user


@router.patch("/patch", response_model=UserResponseModel,
              dependencies=[Depends(access_A)],
              status_code=status.HTTP_202_ACCEPTED)
async def patch_user(body: UserUpdateModel, db: Session = Depends(get_db)):
    user = await repository_users.patch_user(body, db)
    if not user:
        HTTPException(status_code=status.HTTP_404_NOT_FOUND,
                      detail="User not found")
    return user


@router.delete('/delete', response_model=OkResponseModel,
                #dependencies=[Depends(access_A)],
                status_code=status.HTTP_202_ACCEPTED)
async def del_all_users(db: Session = Depends(get_db)):
    users = db.query(User).all()
    for user in users:
        db.delete(user)
        db.commit()

    return {'message': 'ok'}


@router.delete("/delete/{id}",
               dependencies=[Depends(access_A)],
               status_code=status.HTTP_202_ACCEPTED)
async def delete_user(id: int, db: Session = Depends(get_db)):
    return await repository_users.delete_user(id, db)


# @router.post("/create", response_model=UserResponseModel)
# async def create_user(body: UserModel, db: Session=Depends(get_db)):
#     user = await repository_users.create_user(body, db)
#     if not user:
#         return HTTPException(
#             status_code=status.HTTP_404_NOT_FOUND,
#             detail="User hos not been created"
#         )
#     return user




