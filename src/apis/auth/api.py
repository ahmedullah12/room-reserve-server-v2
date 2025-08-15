from fastapi import APIRouter, Depends, HTTPException, Response, Request
import src.apis.auth.schema as schemas
from src.apis.auth.services import AuthService
from src.apis.users.services import UserService
from src.database.main import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/auth")

user_service = UserService()
auth_service = AuthService()

@router.post("/sign-up", response_model=schemas.SignUpResponse)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db), response: Response = None):
    user_exists = user_service.get_user_by_email(db=db, email=user.email)
    
    if user_exists:
        raise HTTPException(status_code=400, detail="User already exists!!")
    
    result = auth_service.sign_up(db=db, user=user)

    # Set the refresh token as a cookie
    response.set_cookie(
        key="refreshToken",
        value=result["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=False
    )

    return {
        "statusCode": 200,
        "success": True,
        "message": "Account created successfully!!",
        "data": {
            "accessToken": result["access_token"],
            "email": result["user"].email
        }
    }

@router.post("/login", response_model=schemas.LoginResponse)
def login(user: schemas.UserLogin, db: Session = Depends(get_db), response: Response = None):
    result = auth_service.login(db=db, user=user)

    # Set the refresh token as a cookie
    response.set_cookie(
        key="refreshToken",
        value=result["refresh_token"],
        httponly=True,
        samesite="lax",
        secure=False
    )

    return {
        "statusCode": 200,
        "success": True,
        "message": "Logged in successfully!!",
        "data": {
            "accessToken": result["access_token"],
            "email": result["user"].email
        }
    }
    
@router.post("/logout")
def logout(response: Response = None):
    response.delete_cookie(key="refreshToken", httponly=True, samesite="lax", secure="false")
    
    return {
        "statusCode": 200,
        "success": True,
        "message": "Logged out successfully!!"
    }
    
@router.post("/refresh-token")
def refresh_token(request: Request, db: Session = Depends(get_db)):
    token = request.cookies.get("refreshToken")
    access_token = auth_service.refreshToken(token=token, db=db)
    
    return {
        "statusCode": 200,
        "success": True,
        "message": "Access token refreshed successfully",
        "data": {
            "accessToken": access_token
        }
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)

