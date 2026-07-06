import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import bcrypt
from app.models.user import User
from app.core.config import settings
from urllib.parse import urlparse

def get_password_hash(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

async def create_user():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    parsed_uri = urlparse(settings.MONGODB_URI)
    db_name = parsed_uri.path.lstrip('/') or "lumina"
    
    await init_beanie(database=client[db_name], document_models=[User])
    
    email = "test@lumina.com"
    existing = await User.find_one(User.email == email)
    
    if existing:
        print(f"User already exists. Email: {email}, Password: User@123")
        return
        
    user = User(
        email=email,
        full_name="Test User",
        hashed_password=get_password_hash("User@123"),
        role="member"
    )
    
    await user.insert()
    print(f"User created successfully. Email: {email}, Password: User@123")

if __name__ == "__main__":
    asyncio.run(create_user())
