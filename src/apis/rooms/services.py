from sqlalchemy.orm import Session
import src.apis.rooms.models as models
import src.apis.rooms.schema as schemas
from fastapi import HTTPException
import math

class RoomServices:
    def get_all_rooms(self, db: Session, skip: int = 0, limit: int = 20):
        total_query = db.query(models.Room)
        total = total_query.count()
        
        rooms_query = db.query(models.Room).offset(skip).limit(limit)
        rooms = rooms_query.all()
        
        page = (skip // limit) + 1 if limit > 0 else 1
        total_pages = math.ceil(total / limit) if limit > 0 else 1
        
        return {
            "data": rooms,
            "meta": {
                "page": page,
                "limit": limit,
                "total": total,
                "totalPage": total_pages
            }
        }
    
    def get_single_room(self, db: Session, room_id: str):
        return db.query(models.Room).filter(models.Room.id == room_id).first()
    
    def create_room(self, db: Session, room: schemas.Room):
        room_data = room.model_dump(
            exclude_unset=True
        )
        
        new_room = models.Room(**room_data)
        db.add(new_room)
        db.commit()
        db.refresh(new_room)
        
        return room
    
    def update_room(self, db: Session, room_id: str, updated_data: schemas.RoomUpdate):
        room = self.get_single_room(db=db, room_id=room_id)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found!!")
        
        updated_room_data = updated_data.model_dump(
            exclude_unset=True
        )
    
        for key, value in updated_room_data.items():
            if hasattr(room, key):
                setattr(room, key, value)
        
        try:
            db.commit()
            db.refresh(room)
            return room
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error updating the room: {str(e)}")
        
    def delete_room(self, db: Session, room_id: str):
        room = self.get_single_room(db=db, room_id=room_id)
        
        if not room:
            raise HTTPException(status_code=404, detail="Room not found!!")
        
        room.isDeleted = True
        
        try:
            db.commit()
            db.refresh(room)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Error deleting the room: {str(e)}")