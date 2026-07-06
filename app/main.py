from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.database import init_db
from app.core.config import settings

from app.models.user import User
from app.models.subscription import Subscription
from app.models.payment import Payment
from app.models.course import Course, UserProgress
from app.models.referral import Referral, Commission, WithdrawalRequest
from urllib.parse import urlparse

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Connect to MongoDB
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    parsed_uri = urlparse(settings.MONGODB_URI)
    db_name = parsed_uri.path.lstrip('/') or "lumina"
    
    await init_beanie(
        database=client[db_name],
        document_models=[
            User,
            Subscription,
            Payment,
            Course,
            UserProgress,
            Referral,
            Commission,
            WithdrawalRequest
        ]
    )
    yield
    # Shutdown

app = FastAPI(
    title=settings.PROJECT_NAME,
    lifespan=lifespan,
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], # Update this in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"message": f"Welcome to {settings.PROJECT_NAME} API"}

from app.api.routes import api_router

app.include_router(api_router, prefix="/api/v1")
