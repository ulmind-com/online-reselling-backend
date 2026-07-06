import asyncio
from motor.motor_asyncio import AsyncIOMotorClient
from beanie import init_beanie
import bcrypt
from app.models.user import User
from app.core.config import settings
from urllib.parse import urlparse

def get_password_hash(password: str) -> str:
    # Use raw bcrypt to avoid passlib issues on newer pythons
    salt = bcrypt.gensalt()
    hashed_bytes = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed_bytes.decode('utf-8')

async def create_admin():
    client = AsyncIOMotorClient(settings.MONGODB_URI)
    
    # Extract DB name from URI or default to lumina
    parsed_uri = urlparse(settings.MONGODB_URI)
    db_name = parsed_uri.path.lstrip('/') or "lumina"
    
    await init_beanie(database=client[db_name], document_models=[User])
    
    admin_email = "admin@lumina.com"
    existing_admin = await User.find_one(User.email == admin_email)
    
    if existing_admin:
        # Update existing admin
        existing_admin.role = "admin"
        existing_admin.hashed_password = get_password_hash("Admin@123")
        await existing_admin.save()
        print(f"Admin user already existed and was reset. Email: {admin_email}, Password: Admin@123")
        return
        
    admin_user = User(
        email=admin_email,
        full_name="Admin User",
        hashed_password=get_password_hash("Admin@123"),
        role="admin"
    )
    
    await admin_user.insert()
    print(f"Admin user created successfully. Email: {admin_email}, Password: Admin@123")

if __name__ == "__main__":
    asyncio.run(create_admin())
