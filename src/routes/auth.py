import logging

from random import randint

from fastapi import APIRouter, Depends, status, HTTPException, Security, BackgroundTasks, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials, OAuth2PasswordRequestForm
from fastapi.responses import JSONResponse
from starlette.responses import RedirectResponse
from sqlalchemy.orm import Session
from google.oauth2 import id_token
from google.auth.transport import requests

from src.schemas import UserRegistrationBase, TokenModel, OkResponseModel, GoogleAuthResp
from src.database.db_connection import get_db
from src.repository import users as repository_users
from src.database.models import User, Token
from src.services.auth import auth_service
from src.services.email import send_email
from src.schemas import TokenModel, RequestEmail
from src.conf.config import settings


router = APIRouter(prefix='/auth', tags=["Auth"])

security = HTTPBearer()


CREDENTIALS_EXCEPTION = HTTPException(
    status_code=status.HTTP_401_UNAUTHORIZED,
    detail='Could not validate credentials',
    headers={'WWW-Authenticate': 'Bearer'},
)



GOOGLE_CLIENT_ID = settings.google_client_id or None
GOOGLE_CLIENT_SECRET = settings.google_client_secret or None
if GOOGLE_CLIENT_ID is None or GOOGLE_CLIENT_SECRET is None:
    raise BaseException('Missing env variables')


logger = logging.getLogger(__name__)



@router.post("/google_auth")
async def google_auth(request: Request,
                      background_tasks: BackgroundTasks,
                      db: Session = Depends(get_db)):

    data = await request.json()
    token = data.get('auth_code')
    bot_auth_code = str(randint(1111, 9999))

    if not token:
        raise HTTPException(status_code=400, detail="Token is missing")

    try:
        idinfo = id_token.verify_oauth2_token(token, requests.Request(), GOOGLE_CLIENT_ID)
    except ValueError as e:
        # Невірний токен
        raise HTTPException(status_code=400, detail="Invalid token")
    
    user = await repository_users.get_user_by_email(idinfo['email'], db)
    if user is None:
        data = GoogleAuthResp(**idinfo)
        user = await repository_users.create_user_by_google_cred(data, db, bot_auth_code)
        background_tasks.add_task(send_email, user.email, user.first_name, request.base_url, bot_auth_code)
        
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    # print({"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"})
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/signup", response_model=OkResponseModel, status_code=status.HTTP_201_CREATED)
async def signup(body: UserRegistrationBase,
                 request: Request,
                 background_tasks: BackgroundTasks, 
                 db: Session = Depends(get_db)) -> User | HTTPException:
    exist_user = await repository_users.get_user_by_email(body.email, db)
    if exist_user:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Account already exists")
    bot_auth_code = str(randint(1111, 9999))
    new_user = await repository_users.create_user(body, db, bot_auth_code)

    logging.basicConfig(level=logging.INFO)
    logger.info(f'start background_tasks')
    background_tasks.add_task(send_email, new_user.email, new_user.first_name, request.base_url, bot_auth_code)
    logger.info("finfsh background_tasks")
    return {"message": "ok"}


@router.post("/login", response_model=TokenModel)
async def logiin(body: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)) -> dict | HTTPException:
    user = await repository_users.get_user_by_email(body.username, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email")
    if not auth_service.verify_password(body.password, user.password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid password")
    if user.banned:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="You are undesirable person.")
    # Generate JWT
    access_token = await auth_service.create_access_token(data={"sub": user.email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": user.email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.post("/logout")
async def logout(token_data: Token = Depends(auth_service.oauth2_scheme), 
                 db: Session = Depends(get_db)) -> JSONResponse:
    await auth_service.add_token_to_blacklist(token_data, db)
    return JSONResponse(content={"message": "Successfully logged out"})


@router.get('/refresh_token', response_model=TokenModel)
async def refresh_token(credentials: HTTPAuthorizationCredentials = Security(security), 
                        db: Session = Depends(get_db)) -> dict | HTTPException:
    token = credentials.credentials
    print(token)
    email = await auth_service.decode_refresh_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user.refresh_token != token:
        await repository_users.update_token(user, None, db)
        raise CREDENTIALS_EXCEPTION
    
    access_token = await auth_service.create_access_token(data={"sub": email})
    refresh_token = await auth_service.create_refresh_token(data={"sub": email})
    await repository_users.update_token(user, refresh_token, db)
    return {"access_token": access_token, "refresh_token": refresh_token, "token_type": "bearer"}


@router.get('/confirmed_email/{token}')
async def confirmed_email(token: str, db: Session = Depends(get_db)):
    email = await auth_service.get_email_from_token(token)
    user = await repository_users.get_user_by_email(email, db)
    if user is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Verification error")
    home_page = settings.home_page
    return RedirectResponse(home_page)
    # if user.confirmed:
    #     return {"message": "Your email is already confirmed"}
    # await repository_users.confirmed_email(email, db)
    # return {"message": "Email confirmed"}


@router.post('/request_email')
async def request_email(body: RequestEmail, background_tasks: BackgroundTasks, request: Request,
                        db: Session = Depends(get_db)):
    user = await repository_users.get_user_by_email(body.email, db)

    if user.confirmed:
        return {"message": "Your email is already confirmed"}
    if user:
        background_tasks.add_task(send_email, user.email, user.username, request.base_url)
    return {"message": "Check your email for confirmation."}