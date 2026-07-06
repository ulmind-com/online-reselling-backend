import stripe
from fastapi import APIRouter, Depends, HTTPException, Request, status
from typing import Any
from app.models.user import User
from app.models.subscription import Subscription, SubscriptionStatus, SubscriptionPlan
from app.models.payment import Payment
from app.api.dependencies.auth import get_current_user
from app.services import stripe_service
from datetime import datetime

router = APIRouter()

@router.post("/checkout-session")
async def create_checkout(price_id: str, ref: str = None, current_user: User = Depends(get_current_user)):
    if not current_user.stripe_customer_id:
        customer = stripe_service.create_customer(current_user)
        current_user.stripe_customer_id = customer.id
        await current_user.save()
        
    referral_connect_id = None
    commission_percent = 20.0 # 20% commission to affiliate
    
    if ref:
        referrer = await User.find_one(User.referral_code == ref)
        if referrer and referrer.stripe_connect_id and referrer.charges_enabled:
            referral_connect_id = referrer.stripe_connect_id
            # Optionally update current user with referred_by_id
            if not current_user.referred_by_id and referrer.id != current_user.id:
                current_user.referred_by_id = referrer.id
                await current_user.save()
        
    session = stripe_service.create_checkout_session(
        customer_id=current_user.stripe_customer_id,
        price_id=price_id,
        success_url="http://localhost:3000/dashboard?session_id={CHECKOUT_SESSION_ID}",
        cancel_url="http://localhost:3000/pricing",
        referral_connect_id=referral_connect_id,
        commission_percent=commission_percent
    )
    return {"url": session.url}

@router.post("/webhook")
async def stripe_webhook(request: Request):
    payload = await request.body()
    sig_header = request.headers.get("stripe-signature")
    
    try:
        event = stripe_service.construct_webhook_event(payload, sig_header)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except stripe.error.SignatureVerificationError as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if getattr(event, "type", None) == "checkout.session.completed":
        session = event.data.object
        customer_id = session.customer
        subscription_id = session.subscription
        # Fetch user
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user and subscription_id:
            stripe_sub = stripe.Subscription.retrieve(subscription_id)
            plan_interval = stripe_sub.plan.interval # 'month' or 'year'
            plan = SubscriptionPlan.MONTHLY if plan_interval == "month" else SubscriptionPlan.YEARLY
            
            sub = Subscription(
                user=user,
                stripe_subscription_id=subscription_id,
                status=SubscriptionStatus(stripe_sub.status),
                plan=plan,
                current_period_start=datetime.fromtimestamp(stripe_sub.current_period_start),
                current_period_end=datetime.fromtimestamp(stripe_sub.current_period_end)
            )
            await sub.insert()
            
            # create initial payment record
            if session.payment_intent:
                payment = Payment(
                    user=user,
                    stripe_charge_id=session.payment_intent,
                    amount=session.amount_total / 100.0,
                    currency=session.currency,
                    status="succeeded"
                )
                await payment.insert()

    elif getattr(event, "type", None) == "invoice.payment_succeeded":
        invoice = event.data.object
        customer_id = invoice.customer
        user = await User.find_one(User.stripe_customer_id == customer_id)
        if user:
            payment = Payment(
                user=user,
                stripe_charge_id=invoice.charge,
                stripe_invoice_id=invoice.id,
                amount=invoice.amount_paid / 100.0,
                currency=invoice.currency,
                status="succeeded",
                receipt_url=invoice.hosted_invoice_url
            )
            await payment.insert()
            
            sub = await Subscription.find_one(Subscription.stripe_subscription_id == invoice.subscription)
            if sub:
                stripe_sub = stripe.Subscription.retrieve(invoice.subscription)
                sub.status = SubscriptionStatus(stripe_sub.status)
                sub.current_period_start = datetime.fromtimestamp(stripe_sub.current_period_start)
                sub.current_period_end = datetime.fromtimestamp(stripe_sub.current_period_end)
                await sub.save()

    elif getattr(event, "type", None) == "customer.subscription.deleted":
        subscription = event.data.object
        sub = await Subscription.find_one(Subscription.stripe_subscription_id == subscription.id)
        if sub:
            sub.status = SubscriptionStatus.CANCELED
            sub.canceled_at = datetime.utcnow()
            await sub.save()

    return {"status": "success"}

@router.get("/current")
async def get_current_subscription(current_user: User = Depends(get_current_user)):
    sub = await Subscription.find_one(Subscription.user.id == current_user.id)
    return sub
