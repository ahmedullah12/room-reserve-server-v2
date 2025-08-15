from fastapi import APIRouter, Depends, HTTPException
import src.apis.users.schema as schemas
from src.apis.users.services import UserService
from src.database.main import get_db
from sqlalchemy.orm import Session

router = APIRouter(prefix="/users")

services = UserService()

@router.get("/users")
def get_all_users(db: Session = Depends(get_db)):
    users = services.get_users(db=db)
    
    return {
        "message": "Users fetched successfully!!",
        "users": users
    }
    
@router.get("/users/{user_id}")
def get_user(user_id: str, db: Session = Depends(get_db)):
    user = services.get_user(db, user_id)
    
    return {
        "message": "User fetched successfully!!",
        "user": user
    }
    
@router.patch("/update-user/{user_id}")
def update_user(user_id: str, updated_data: schemas.UserUpdate, db: Session = Depends(get_db)):
    updated_user = services.update_user(db, user_id, user_data=updated_data)
    
    return {
        "message": "Users updated successfully!!",
        "user": updated_user
    }

@router.delete("/delete-user/{user_id}")
def delete_user(user_id: str, db: Session = Depends(get_db)):
    services.delete_user(db, user_id)
    
    return {
        "message": "User deleted successfully!!"
    }
    
@router.put("/make-admin/{user_id}")
def make_admin(user_id: str, db: Session = Depends(get_db)):
    services.make_admin(db, user_id)
    
    return {
        "message": "User role updated successfully!!"
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(router, host="0.0.0.0", port=8000)

