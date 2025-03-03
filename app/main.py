from fastapi import FastAPI
from contextlib import asynccontextmanager
from app.database.database import init_db

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield

app = FastAPI(lifespan=lifespan)

@app.get("/")
async def root():
    return {"message": "FastAPI CRUD Challenge"}