from fastapi import FastAPI
import uvicorn
from app.core.database import Base, engine
from app.models.refresh_token import RefreshToken
from app.routers.auth import router as auth_router
from app.routers.users import router as users_router

Base.metadata.create_all(bind=engine)

app = FastAPI()

app.include_router(auth_router)
app.include_router(users_router)

@app.get("/")
async def read_root():
    return {"message": "Welcome to the FastAPI Boilerplate Services !"}

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8809, reload=True)