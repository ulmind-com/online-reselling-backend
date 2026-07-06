from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel
from typing import Optional
from app.models.user import User
from app.api.dependencies.auth import get_current_user
from app.services import stripe_service
import stripe

router = APIRouter()

class StripeConnectResponse(BaseModel):
    url: str

class ConnectStatusResponse(BaseModel):
    is_connected: bool
    charges_enabled: bool
    stripe_connect_id: Optional[str] = None

@router.post("/onboard", response_model=StripeConnectResponse)
async def create_onboarding_link(current_user: User = Depends(get_current_user)):
    try:
        # Create a connected account if they don't have one
        if not current_user.stripe_connect_id:
            account = stripe_service.create_connect_account(current_user.email)
            current_user.stripe_connect_id = account.id
            await current_user.save()
            
        # Create an account link for onboarding
        account_link = stripe_service.create_account_link(
            account_id=current_user.stripe_connect_id,
            return_url="http://localhost:3000/dashboard/earnings?onboarded=true",
            refresh_url="http://localhost:3000/dashboard/earnings?refresh=true"
        )
        
        return {"url": account_link.url}
        
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )

@router.get("/status", response_model=ConnectStatusResponse)
async def get_connect_status(current_user: User = Depends(get_current_user)):
    if not current_user.stripe_connect_id:
        return {
            "is_connected": False,
            "charges_enabled": False,
            "stripe_connect_id": None
        }
        
    try:
        # Verify status with Stripe API
        account = stripe.Account.retrieve(current_user.stripe_connect_id)
        if account.charges_enabled != current_user.charges_enabled:
            current_user.charges_enabled = account.charges_enabled
            await current_user.save()
            
        return {
            "is_connected": True,
            "charges_enabled": current_user.charges_enabled,
            "stripe_connect_id": current_user.stripe_connect_id
        }
    except stripe.error.StripeError as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e)
        )
