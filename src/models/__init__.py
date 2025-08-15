# src/models/__init__.py
from src.database.main import Base

# Import all models to register them
from src.apis.users.models import *
from src.apis.rooms.models import *