"""Billing router for Stripe webhooks and subscription management."""

from datetime import datetime

import stripe
from fastapi import APIRouter, Depends, Header, HTTPException, Request, status
from pydantic import BaseModel
from sqlalchemy import select, update
from sqlalchemy.ext.asyncio import AsyncSession

from app.config import get_settings
from app.database import get_db
from app.middleware.auth import RequiredUser
from app.models import User, Subscription

router = APIRouter(prefix="/v1/billing", tags=["billing"])
settings = get_settings()

# Initialize Stripe
stripe.api_key = settings.stripe_secret_key


class CreateCheckoutResponse(BaseModel):
    """Response for checkout session creation."""

    checkout_url: str
    session_id: str


class PortalResponse(BaseModel):
    """Response for customer portal."""

    portal_url: str


@router.post("/checkout", response_model=CreateCheckoutResponse)
async def create_checkout_session(
    current_user: RequiredUser,
    interval: str = "month",  # "month" or "year"
    db: AsyncSession = Depends(get_db),
) -> CreateCheckoutResponse:
    """
    Create a Stripe checkout session for Pro subscription.

    Args:
        interval: Billing interval - "month" or "year"
    """
    if current_user.is_pro:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="You already have a Pro subscription",
        )

    # Get or create Stripe customer
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found",
        )

    # Create or retrieve Stripe customer
    if user.stripe_customer_id:
        customer_id = user.stripe_customer_id
    else:
        customer = stripe.Customer.create(
            email=user.email,
            name=user.name,
            metadata={"user_id": str(user.id)},
        )
        customer_id = customer.id

        # Save customer ID
        await db.execute(
            update(User)
            .where(User.id == user.id)
            .values(stripe_customer_id=customer_id)
        )
        await db.commit()

    # Determine price ID
    price_id = (
        settings.stripe_price_yearly
        if interval == "year"
        else settings.stripe_price_monthly
    )

    if not price_id:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Stripe prices not configured",
        )

    # Create checkout session
    session = stripe.checkout.Session.create(
        customer=customer_id,
        mode="subscription",
        line_items=[{"price": price_id, "quantity": 1}],
        success_url="https://slimpdf.io/dashboard?success=true",
        cancel_url="https://slimpdf.io/pricing?canceled=true",
        metadata={"user_id": str(user.id)},
    )

    return CreateCheckoutResponse(
        checkout_url=session.url,
        session_id=session.id,
    )


@router.post("/portal", response_model=PortalResponse)
async def create_portal_session(
    current_user: RequiredUser,
    db: AsyncSession = Depends(get_db),
) -> PortalResponse:
    """
    Create a Stripe customer portal session for subscription management.
    """
    result = await db.execute(
        select(User).where(User.id == current_user.id)
    )
    user = result.scalar_one_or_none()

    if not user or not user.stripe_customer_id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No billing account found",
        )

    session = stripe.billing_portal.Session.create(
        customer=user.stripe_customer_id,
        return_url="https://slimpdf.io/dashboard",
    )

    return PortalResponse(portal_url=session.url)


@router.post("/webhook")
async def stripe_webhook(
    request: Request,
    stripe_signature: str = Header(None, alias="Stripe-Signature"),
    db: AsyncSession = Depends(get_db),
):
    """
    Handle Stripe webhook events.

    Events handled:
    - checkout.session.completed: New subscription
    - customer.subscription.updated: Subscription changes
    - customer.subscription.deleted: Subscription canceled
    """
    if not stripe_signature:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Missing Stripe signature",
        )

    payload = await request.body()

    try:
        event = stripe.Webhook.construct_event(
            payload,
            stripe_signature,
            settings.stripe_webhook_secret,
        )
    except stripe.error.SignatureVerificationError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid signature",
        )

    # Handle events
    if event.type == "checkout.session.completed":
        session = event.data.object
        user_id = session.metadata.get("user_id")

        if user_id and session.subscription:
            # Get subscription details
            subscription = stripe.Subscription.retrieve(session.subscription)

            # Update user plan
            await db.execute(
                update(User)
                .where(User.id == user_id)
                .values(plan="pro")
            )

            # Create subscription record
            sub = Subscription(
                user_id=user_id,
                stripe_subscription_id=subscription.id,
                status=subscription.status,
                plan_interval=subscription.items.data[0].price.recurring.interval,
                current_period_start=datetime.fromtimestamp(
                    subscription.current_period_start
                ),
                current_period_end=datetime.fromtimestamp(
                    subscription.current_period_end
                ),
            )
            db.add(sub)
            await db.commit()

    elif event.type == "customer.subscription.updated":
        subscription = event.data.object

        # Update subscription record
        await db.execute(
            update(Subscription)
            .where(Subscription.stripe_subscription_id == subscription.id)
            .values(
                status=subscription.status,
                current_period_start=datetime.fromtimestamp(
                    subscription.current_period_start
                ),
                current_period_end=datetime.fromtimestamp(
                    subscription.current_period_end
                ),
                cancel_at_period_end=subscription.cancel_at_period_end,
                updated_at=datetime.utcnow(),
            )
        )
        await db.commit()

    elif event.type == "customer.subscription.deleted":
        subscription = event.data.object

        # Update subscription status
        await db.execute(
            update(Subscription)
            .where(Subscription.stripe_subscription_id == subscription.id)
            .values(
                status="canceled",
                updated_at=datetime.utcnow(),
            )
        )

        # Downgrade user to free
        result = await db.execute(
            select(Subscription).where(
                Subscription.stripe_subscription_id == subscription.id
            )
        )
        sub = result.scalar_one_or_none()

        if sub:
            await db.execute(
                update(User)
                .where(User.id == sub.user_id)
                .values(plan="free")
            )

        await db.commit()

    return {"status": "ok"}
