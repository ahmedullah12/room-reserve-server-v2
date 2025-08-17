from fastapi import APIRouter, Depends
import src.apis.rooms.schema as schemas
from src.apis.rooms.services import RoomServices
from sqlalchemy.orm import Session
from src.database.main import get_db

router = APIRouter(prefix="/rooms")

room_services = RoomServices()

@router.post("")
async def create_room(room: schemas.Room, db: Session = Depends(get_db)):
    room_data = room_services.create_room(db, room)

    return {
        "statusCode": 201,
        "success": True,
        "message": "Room created successfully!!",
        "data": room_data
    }


@router.get("")
async def get_all_room(db: Session = Depends(get_db)):
    data = room_services.get_all_rooms(db=db, skip=0, limit=50)

    return {
        "statusCode": 200,
        "success": True,
        "message": "Rooms fetched successfully!!",
        "data": data["data"],
        "meta": data["meta"]
    }


@router.get("/:id")
async def get_single_room(id: str, db: Session = Depends(get_db)):
    room = room_services.get_single_room(db=db, room_id=id)

    return {
        "statusCode": 200,
        "success": True,
        "message": "Room fetched successfully!!",
        "data": room
    }


@router.put("/:id")
async def update_room(id: str, updated_data: schemas.RoomUpdate, db: Session = Depends(get_db), ):
    updated_room = room_services.update_room(
        db, room_id=id, updated_data=updated_data)

    return {
        "success": True,
        "statusCode": 200,
        "message": "Room updated successfully",
        "data": updated_room
    }


@router.delete("/:id")
async def delete_room(id: str, db: Session = Depends(get_db)):
    await room_services.delete_room(d=db, room_id=id)

    return {
        "success": True,
        "statusCode": 200,
        "message": "Room deleted successfully",
    }
