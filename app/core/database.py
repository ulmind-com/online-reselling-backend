from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
from app.core.config import settings
import urllib.parse
from typing import List

# We will add models here as we create them
# e.g. from app.models.user import User

async def init_db(models: List = []):
    uri = settings.MONGODB_URI
    
    # Motor doesn't like unescaped @ in password, let's make sure it's properly handled if we manually parse, 
    # but since the connection string might already be URL encoded or has the @ escaped, we pass it directly first.
    # The user provided: mongodb+srv://paymentgayway:abc@123@cluster0.2jtvuoz.mongodb.net/
    client = AsyncIOMotorClient(uri)
    # the database name can be parsed from uri or we default to `lumina_db`
    db = client.get_default_database(default="lumina_db")
    
    if models:
        await init_beanie(database=db, document_models=models)
