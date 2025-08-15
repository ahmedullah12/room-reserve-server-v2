from fastapi import APIRouter, Depends
import src.apis.rooms.schema as schemas
from src.apis.rooms.services import RoomServices
from sqlalchemy.orm import Session
from src.database.main import get_db

router = APIRouter(prefix="/rooms")

room_services = RoomServices()

@router.post("")
def create_room(room: schemas.Room, db: Session = Depends(get_db)):
    room_data = room_services.create_room(db, room)

    return {
        "statusCode": 201,
        "success": True,
        "message": "Room created successfully!!",
        "data": room_data
    }
