from fastapi import APIRouter, Depends, HTTPException
import src.apis.rooms.models as models
import src.apis.rooms.schema as schemas
from src.apis.rooms.services import RoomServices
from sqlalchemy.orm import Session
from src.database.main import get_db
from typing import List
from datetime import datetime

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

@router.post("/chat/message", response_model=schemas.ChatResponse)
async def chat_with_ai(
    chat_request: schemas.ChatRequest,
    db: Session = Depends(get_db)
):
    if not chat_request.message or not chat_request.message.strip():
        raise HTTPException(status_code=400, detail="Message cannot be empty")
    
    try:
        ai_response = await room_services.get_ai_response(chat_request.message, db)
    except:
        return {
            "message": "Having issues"
        }
    
    chat_message = models.ChatMessage(
        user_id=chat_request.user_id,
        message=chat_request.message,
        response=ai_response
    )
    db.add(chat_message)
    db.commit()
    db.refresh(chat_message)
    
    return schemas.ChatResponse(
        response=ai_response,
        timestamp=chat_message.timestamp,
        message_id=chat_message.id,
        success=True
    )
@router.get("/chat/messages/{user_id}", response_model=List[schemas.ChatMessageOut])
async def get_user_messages(user_id: str, db: Session = Depends(get_db)):
    messages = db.query(models.ChatMessage).filter(
        models.ChatMessage.user_id == user_id
    ).order_by(models.ChatMessage.timestamp.asc()).all()
    
    if not messages:
        try:
            room_count = db.query(models.Room).filter(
                models.Room.isDeleted == False
            ).count()
        except:
            room_count = "several"
        
        welcome_messages = [
            f"Hello there! 😊 I'm Sarah, your friendly room booking assistant. We have {room_count} amazing rooms available right now. I'm here to help you find the perfect one - just tell me what you're looking for!",
            
            f"Hi! Welcome! I'm Sarah and I'm so excited to help you find an incredible room today. With {room_count} fantastic options available, I know we'll find something perfect for you. What can I help you with?",
            
            f"Hey there! Great to meet you! 🌟 I'm Sarah, your personal room booking assistant. We've got {room_count} wonderful rooms ready for booking. Whether you need something cozy or spacious, budget-friendly or luxurious - I'm here to help! What are you looking for?",
            
            f"Hello! I'm Sarah, and I absolutely love helping people find their perfect room! ✨ We currently have {room_count} available rooms with different amenities, sizes, and price points. What would make your ideal room? Let's find it together!"
        ]
        
        import hashlib
        user_hash = int(hashlib.md5(user_id.encode()).hexdigest(), 16)
        selected_message = welcome_messages[user_hash % len(welcome_messages)]
        
        default_message = models.ChatMessage(
            user_id=user_id,
            response=selected_message,
            is_bot_message=True,
            timestamp=datetime.utcnow()
        )
        db.add(default_message)
        db.commit()
        messages = [default_message]
    
    return messages

@router.delete("/chat/messages/{user_id}")
async def clear_user_messages(user_id: str, db: Session = Depends(get_db)):
    db.query(models.ChatMessage).filter(models.ChatMessage.user_id == user_id).delete()
    db.commit()
    return {"message": "Chat history cleared"}