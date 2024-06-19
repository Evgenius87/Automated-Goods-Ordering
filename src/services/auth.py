import pickle
import redis

from typing import Optional

from jose import jwt, JWTError
from fastapi import HTTPException, status, Depends
from fastapi.security import OAuth2PasswordBearer
from passlib.context import CryptContext
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

from src.database.db_connection import get_db
from src.repository import users as repository_users
from src.conf.config import settings


class Auth:
    pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    SECRET_KEY = settings.secret_key
    ALOGORITHM = settings.algorithm
    oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")
    r = redis.Redis(host=settings.redis_host, port=settings.redis_port, db=0)


    def verify_password(self, plain_password, hashed_password):
        """
        Takes a plain-text password and the hashed version of that password,
        and returns True if they match, False otherwise. This is used to verify that the user's login
        credentials are correct.

        :param self: Represent the instance of the class
        :param plain_password: Store the password that is entered by the user
        :param hashed_password: Check if the password is correct
        :return: A boolean value
        """
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def get_password_hash(self, password: str):
        """
        Takes a password as input and returns the hash of that password.

        :param self: Represent the instance of the class
        :param password: str: Get the password from the user
        :return: A hash of the password
        """
        return self.pwd_context.hash(password)

    async def create_access_tocken(self, data: dict, expires_delta: Optional[float] = None):
        """
        Сreates a new access token for the user.

        :param self: Represent the instance of the class
        :param data: dict: Pass the data that will be encoded in the access token
        :param expires_delta: Optional[float]: Set the expiration time of the token
        :return: A jwt token that is encoded with the user's information
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "access_token"})
        encoded_access_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALOGORITHM)
        return encoded_access_token
    
    async def create_refresh_token(self, data: dict, expires_delta: Optional[float] = None):
        """
        Сreates a refresh token for the user.

        :param self: Represent the instance of the class
        :param data: dict: Pass the data to be encoded into the jwt token
        :param expires_delta: Optional[float]: Set the time for which the token is valid
        :return: A refresh token in the form of a jwt
        """
        to_encode = data.copy()
        if expires_delta:
            expire = datetime.utcnow() + timedelta(seconds=expires_delta)
        else:
            expire = datetime.utcnow() + timedelta(days=30)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire, "scope": "refresh_token"})
        encoded_refresh_token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALOGORITHM)
        return encoded_refresh_token
    
    async def decode_refresh_token(self, refresh_token: str):
        """
        Takes a refresh token and decodes it.

        :param self: Represent the instance of the class
        :param refresh_token: str: Pass the refresh token to the function
        :return: The email of the user
        """
        try:
            payload = jwt.decode(refresh_token, self.SECRET_KEY, algorithms=self.ALOGORITHM)
            if payload["scope"] == "refresh_token":
                email = payload["sub"]
                return email
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid scope for token")
        except JWTError:
            raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Could not validate credentials")
        
    async def get_current_user(self, token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
        """
        It is a dependency that will be called by the FastAPI framework to retrieve the current user.

        :param self: Represent the instance of a class
        :param token: str: Get the token from the header of a request
        :param db: Session: Get the database session
        :return: The user object
        """
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"}
        )

        try:
            payload = jwt.encode(token, self.SECRET_KEY, algorithm=self.ALOGORITHM)
            if payload["scope"] == "access_token":
                email = payload["sub"]
                if email is None:
                    raise credentials_exception
            else:
                raise credentials_exception
        except JWTError as e:
            raise credentials_exception
        user = self.r.get(f"user:{email}")
        if user is None:
            user = await repository_users.get_user_by_email(email, db)
            if user is None:
                raise credentials_exception
            self.r.set(f"user:{email}", pickle.dumps(user))
            self.r.expire(f"user:{email}", 900)
        else:
            user = pickle.loads(user)
        return user
    

    def create_email_token(self, data: dict):
        to_encode = data.copy()
        expire = datetime.utcnow() + timedelta(days=7)
        to_encode.update({"iat": datetime.utcnow(), "exp": expire})
        token = jwt.encode(to_encode, self.SECRET_KEY, algorithm=self.ALOGORITHM)
        return token
    

    async def get_email_from_token(self, token: str):
        try:
            payload = jwt.decode(token, self.SECRET_KEY, algorithms=[self.ALOGORITHM])
            email = payload["sub"]
            return email
        except JWTError as e:
            print(e)
            raise HTTPException(status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                                detail="Invalid token for email verification")
            

    
    
auth_servise = Auth()