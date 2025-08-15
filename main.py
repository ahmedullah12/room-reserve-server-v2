from fastapi import FastAPI
from src.apis.auth.api import router as auth_router
from src.apis.users.api import router as user_router

app = FastAPI(
    title="Room Reservation",
    description="Service for booking meeting rooms",
)

app.include_router(auth_router, tags=["auth"])
app.include_router(user_router, tags=["users"])

@app.get("/")
def root_route():
    return {"message": "Server is running..."}