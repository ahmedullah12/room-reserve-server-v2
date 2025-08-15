from sqlalchemy.orm import Session
import src.apis.rooms.models as models
import src.apis.rooms.schema as schemas

class RoomServices:
    def get_all_rooms(self, db: Session, skip: int = 0, limit: int = 20):
        return db.query(models.Room).offset(skip).limit(limit).all()
    
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
    
    