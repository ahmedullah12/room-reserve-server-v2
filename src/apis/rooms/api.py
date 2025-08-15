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

@router.get("")
def get_all_room(db: Session = Depends(get_db)):
    rooms = room_services.get_all_rooms(db=db, skip=0, limit=50)
    
    return {
        "statusCode": 200,
        "success": True,
        "message": "Rooms fetched successfully!!",
        "data": rooms
    }
    
@router.get("/:id")
def get_single_room(id: str, db: Session = Depends(get_db)):
    room = room_services.get_single_room(db=db, room_id=id)
    
    return {
        "statusCode": 200,
        "success": True,
        "message": "Room fetched successfully!!",
        "data": room
    }