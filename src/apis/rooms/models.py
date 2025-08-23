from sqlalchemy import Column, String, Integer, Boolean, DateTime, Text
from src.database.main import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY 
from datetime import datetime

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String)
    roomNumber= Column(Integer)
    floorNo = Column(Integer)
    capacity = Column(Integer)
    pricePerSlot = Column(Integer)
    description = Column(String)
    images = Column(MutableList.as_mutable(ARRAY(String)), default=list)
    amenities = Column(MutableList.as_mutable(ARRAY(String)), default=list)
    isDeleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  
    

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    message = Column(Text, nullable=False)
    response = Column(Text, nullable=False)
    timestamp = Column(DateTime, default=datetime.utcnow)
    is_bot_message = Column(Boolean, default=False)