from fastapi import APIRouter
from app.api.routes import auth
from app.api.routes import subscriptions
from app.api.routes import users
from app.api.routes import courses
from app.api.routes import referrals
from app.api.routes import stripe_connect
from app.api.routes import products
from app.api.routes import categories

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(subscriptions.router, prefix="/subscriptions", tags=["subscriptions"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(courses.router, prefix="/courses", tags=["courses"])
api_router.include_router(referrals.router, prefix="/referrals", tags=["referrals"])
api_router.include_router(stripe_connect.router, prefix="/connect", tags=["stripe-connect"])
api_router.include_router(products.router, prefix="/products", tags=["products"])
api_router.include_router(categories.router, prefix="/categories", tags=["categories"])
