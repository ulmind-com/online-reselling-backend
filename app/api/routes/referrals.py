from fastapi import APIRouter, Depends, HTTPException
from typing import List, Dict, Any
from app.models.user import User
from app.models.referral import Referral, Commission, WithdrawalRequest, CommissionStatus
from app.api.dependencies.auth import get_current_active_user, get_current_admin
from pydantic import BaseModel

router = APIRouter()

class WithdrawalRequestCreate(BaseModel):
    amount: float

@router.get("/stats")
async def get_referral_stats(current_user: User = Depends(get_current_active_user)):
    # Get total referrals
    referrals = await Referral.find(Referral.inviter_id == current_user.id).to_list()
    total_referrals = len(referrals)
    
    # Get commissions
    commissions = await Commission.find(Commission.user_id == current_user.id).to_list()
    
    total_earnings = sum(c.amount for c in commissions if c.status in [CommissionStatus.APPROVED, CommissionStatus.PAID])
    pending_earnings = sum(c.amount for c in commissions if c.status == CommissionStatus.PENDING)
    
    return {
        "referral_code": current_user.referral_code,
        "total_referrals": total_referrals,
        "total_earnings": total_earnings,
        "pending_earnings": pending_earnings
    }

@router.get("/commissions")
async def get_commissions(current_user: User = Depends(get_current_active_user)):
    commissions = await Commission.find(Commission.user_id == current_user.id).to_list()
    return commissions

@router.post("/withdraw")
async def request_withdrawal(
    req: WithdrawalRequestCreate, 
    current_user: User = Depends(get_current_active_user)
):
    # Check if they have enough approved/pending earnings 
    # For a real system, you'd only allow withdrawal of APPROVED, not PENDING.
    commissions = await Commission.find(
        Commission.user_id == current_user.id,
        Commission.status == CommissionStatus.APPROVED
    ).to_list()
    
    available_balance = sum(c.amount for c in commissions)
    
    if req.amount > available_balance:
        raise HTTPException(status_code=400, detail="Insufficient approved balance")
        
    withdrawal = WithdrawalRequest(
        user_id=current_user.id,
        amount=req.amount,
        status=CommissionStatus.PENDING
    )
    await withdrawal.insert()
    
    return {"message": "Withdrawal request submitted successfully", "id": str(withdrawal.id)}

@router.get("/info/{code}")
async def get_referrer_info(code: str):
    user = await User.find_one(User.referral_code == code)
    if not user:
        raise HTTPException(status_code=404, detail="Referrer not found")
        
    return {
        "full_name": user.full_name,
        "profile_image": user.profile_image,
        "is_active_affiliate": user.charges_enabled
    }

# --- Admin Routes ---

@router.get("/withdrawals")
async def get_all_withdrawals(admin: User = Depends(get_current_admin)):
    withdrawals = await WithdrawalRequest.find_all().to_list()
    return withdrawals
