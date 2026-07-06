import stripe
from app.core.config import settings
from app.models.user import User

stripe.api_key = settings.STRIPE_SECRET_KEY

def create_customer(user: User):
    customer = stripe.Customer.create(
        email=user.email,
        name=user.full_name,
        metadata={"user_id": str(user.id)}
    )
    return customer

def create_checkout_session(customer_id: str, price_id: str, success_url: str, cancel_url: str, referral_connect_id: str = None, commission_percent: float = 30.0):
    session_kwargs = {
        "customer": customer_id,
        "payment_method_types": ['card'],
        "line_items": [{
            'price': price_id,
            'quantity': 1,
        }],
        "mode": 'subscription',
        "success_url": success_url,
        "cancel_url": cancel_url,
    }
    
    # If a referral connect ID is provided, setup automated split payments via Stripe Connect Destination Charges
    if referral_connect_id:
        session_kwargs["subscription_data"] = {
            "transfer_data": {
                "destination": referral_connect_id,
                "amount_percent": commission_percent
            }
        }

    session = stripe.checkout.Session.create(**session_kwargs)
    return session

def construct_webhook_event(payload: bytes, sig_header: str):
    return stripe.Webhook.construct_event(
        payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
    )

def create_connect_account(email: str):
    return stripe.Account.create(
        type="express",
        email=email,
        capabilities={
            "card_payments": {"requested": True},
            "transfers": {"requested": True},
        },
    )

def create_account_link(account_id: str, return_url: str, refresh_url: str):
    return stripe.AccountLink.create(
        account=account_id,
        refresh_url=refresh_url,
        return_url=return_url,
        type="account_onboarding",
    )
