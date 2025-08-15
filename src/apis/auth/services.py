from sqlalchemy.orm import Session
import src.apis.users.models as models
import src.apis.auth.schema as schemas
from passlib.context import CryptContext
from src.apis.users.services import UserService
from fastapi import HTTPException
from typing import Optional, Dict, Any
from datetime import datetime, timedelta, timezone
import os
import jwt


user_service = UserService()


class AuthService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
        self.access_token_secret = os.getenv("ACCESS_TOKEN_SECRET")
        self.refresh_token_secret = os.getenv("REFRESH_TOKEN_SECRET")
        self.token_algorithm = os.getenv("TOKEN_ALGORITHM")
    
    def get_password_hash(self, password: str) -> str:
        """Hash a password using bcrypt."""
        return self.pwd_context.hash(password)
    
    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify a password against its hash."""
        return self.pwd_context.verify(plain_password, hashed_password)
    
    def create_jwt_token(self, jwt_payload: Dict[str, Any], secret: str, expired_date: timedelta) -> str:
        to_encode = jwt_payload.copy()
        expire = datetime.now(timezone.utc) + expired_date
        to_encode.update({"exp": expire})
        
        encoded_jwt = jwt.encode(to_encode, secret, algorithm=self.token_algorithm)
        return encoded_jwt
    
    def verify_token(self, token: str, secret: str) -> Dict[str, Any]:
        try:
            jwt_payload = jwt.decode(token, secret, algorithms=self.token_algorithm)
            return jwt_payload
        except jwt.ExpiredSignatureError:
            raise HTTPException(status_code=401, detail="Token expired!!")
        except jwt.PyJWTError:
            raise HTTPException(status_code=401, detail="Could not validate token")
            
    def create_access_token(self, jwt_payload: Dict[str, Any]) -> str:
        """Create an access token with 1 day expiration."""
        return self.create_jwt_token(jwt_payload, self.access_token_secret, expired_date=timedelta(days=1))
    
    def create_refresh_token(self, jwt_payload: Dict[str, Any]) -> str:
        """Create a refresh token with 30 days expiration."""
        return self.create_jwt_token(jwt_payload, self.refresh_token_secret, expired_date=timedelta(days=30))
    
    def verify_access_token(self, token: str) -> Dict[str, Any]:
        """Verify an access token."""
        return self.verify_token(token, self.access_token_secret)
    
    def verify_refresh_token(self, token: str) -> Dict[str, Any]:
        """Verify a refresh token."""
        return self.verify_token(token, self.refresh_token_secret)
    
    def sign_up(self, db: Session, user: schemas.UserCreate):
        hashed_password = self.get_password_hash(user.password)

        user_data = user.model_dump(
            exclude_unset=True,
            exclude=["password"]
        )

        new_user = models.User(**user_data, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)

        jwt_payload = {
            "sub": str(new_user.id),
            "email": new_user.email,
            "name": new_user.name,
            "role": str(new_user.role)
        }

        access_token = self.create_access_token(jwt_payload)
        refresh_token = self.create_refresh_token(jwt_payload)

        return {
            "message": "User created successfully!!",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": new_user
        }
        
    def login(self, db: Session, user: schemas.UserLogin):
        user_data = user_service.get_user_by_email(db, user.email)

        if not user_data:
            raise HTTPException(status_code=404, detail="User not found!!")

        password_correct = self.verify_password(user.password, user_data.password)

        if not password_correct:
            raise HTTPException(status_code=401, detail="Password is incorrect!!")

        jwt_payload = {
            "sub": str(user_data.id),
            "email": user_data.email,
            "name": user_data.name,
            "role": str(user_data.role)
        }

        access_token = self.create_access_token(jwt_payload)
        refresh_token = self.create_refresh_token(jwt_payload)

        return {
            "message": "Logged in successfully!!",
            "access_token": access_token,
            "refresh_token": refresh_token,
            "user": user_data
        }
    
    def refreshToken(self, token: str, db: Session):
        secret = self.refresh_token_secret
        payload = self.verify_token(token=token, secret=secret)
        
        if not payload:
            raise HTTPException(status_code=401, detail="Invalid token!!")
        
        user = user_service.get_user(db=db, user_id=payload["sub"])
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found!!")
        
        jwt_payload = {
            "sub": str(user.id),
            "email": user.email,
            "name": user.name,
            "role": str(user.role)
        }
        
        access_token = self.create_access_token(jwt_payload=jwt_payload)
        
        return access_token
        
        
