from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class Room(BaseModel):
    name: str
    roomNumber: int
    floorNo: int
    capacity: int
    price_per_slot: int
    description: str
    images: list[str]
    amenities: list[str]
    
class RoomUpdate(BaseModel):
    name:         Optional[str]   = None
    roomNumber:   Optional[int]   = None
    floorNo:      Optional[int]   = None
    capacity:     Optional[int]   = None
    price_per_slot: Optional[int]   = None
    description: Optional[int] = None
    images:       Optional[list[str]] = None
    amenities:    Optional[list[str]] = None
    
class ChatRequest(BaseModel):
    message: str
    user_id: str

class ChatResponse(BaseModel):
    success: bool
    response: str
    timestamp: datetime
    message_id: str

class ChatMessageOut(BaseModel):
    id: str
    user_id: str
    message: str
    response: str
    timestamp: datetime
    is_bot_message: bool