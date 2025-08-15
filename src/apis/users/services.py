from sqlalchemy.orm import Session
import src.apis.users.models as models
import src.apis.users.schema as schemas
from passlib.context import CryptContext
from typing import Optional, List, Any, Dict
from fastapi import HTTPException


class UserService:
    def __init__(self):
        self.pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
    
    def get_user(self, db: Session, user_id: str) -> Optional[models.User]:
        """Get a user by ID."""
        return db.query(models.User).filter(models.User.id == user_id).first()
    
    def get_user_by_email(self, db: Session, email: str) -> Optional[models.User]:
        """Get a user by email address."""
        return db.query(models.User).filter(models.User.email == email).first()
    
    def get_users(self, db: Session, skip: int = 0, limit: int = 20) -> List[models.User]:
        """Get a list of users with pagination."""
        return db.query(models.User).offset(skip).limit(limit).all()
    
    def update_user(self, db: Session, user_id: str, user_data: schemas.UserUpdate) -> Optional[models.User]:
        """Update a user by ID."""
        user = self.get_user(db, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found!!")
        
        # Convert UserUpdate model to dict, excluding unset values
        update_data = user_data.model_dump(exclude_unset=True)
        
        # If password is being updated, hash it
        if "password" in update_data and update_data["password"]:
            update_data["password"] = self.pwd_context.hash(update_data["password"])
        
        # Update user attributes
        for key, value in update_data.items():
            if hasattr(user, key):
                setattr(user, key, value)
        
        try:
            db.commit()
            db.refresh(user)
            return user
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error updating user: {str(e)}")
    
    def delete_user(self, db: Session, user_id: str) -> bool:
        user = self.get_user(db, user_id)
        if not user:
            raise HTTPException(status_code=404, detail="User not found")
        
        try:
            db.delete(user)
            db.commit()
            return True
        except Exception as e:
            db.rollback()
            raise HTTPException(status_code=400, detail=f"Error deleting user: {str(e)}")
        
    def make_admin(self, db: Session, user_id: str):
        user = self.get_user(db, user_id)
        
        if not user:
            raise HTTPException(status_code=404, detail="User not found!!")
        
        user.role = "admin"
        db.commit()
        db.refresh(user)
        
        return user
        