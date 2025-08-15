from sqlalchemy import Column, String, Integer, Boolean, DateTime
from src.database.main import Base
from sqlalchemy.dialects.postgresql import UUID
import uuid
from sqlalchemy.sql import func
from sqlalchemy.ext.mutable import MutableList
from sqlalchemy.dialects.postgresql import ARRAY

class Room(Base):
    __tablename__ = "rooms"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4, unique=True, nullable=False)
    name = Column(String)
    roomNumber= Column(Integer)
    floorNo = Column(Integer)
    capacity = Column(Integer)
    pricePerSlot = Column(Integer)
    images = Column(MutableList.as_mutable(ARRAY(String)), default=list)
    amenities = Column(MutableList.as_mutable(ARRAY(String)), default=list)
    isDeleted = Column(Boolean, default=False)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())  