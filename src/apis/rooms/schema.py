from pydantic import BaseModel
from typing import Optional

class Room(BaseModel):
    name: str
    roomNumber: int
    floorNo: int
    capacity: int
    pricePerSlot: int
    images: list[str]
    amenities: list[str]
    
class RoomUpdate(BaseModel):
    name:         Optional[str]   = None
    roomNumber:   Optional[int]   = None
    floorNo:      Optional[int]   = None
    capacity:     Optional[int]   = None
    pricePerSlot: Optional[int]   = None
    images:       Optional[list[str]] = None
    amenities:    Optional[list[str]] = None