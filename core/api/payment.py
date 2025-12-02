from fastapi import APIRouter, Depends, HTTPException, Request, Header
from sqlalchemy.ext.asyncio import AsyncSession
from shared.db import get_session
from shared.models.user import User
from core.services.auth import get_current_user
from core.services.stripe_service import stripe_service
from core.config import config
import logging

router = APIRouter()
logger = logging.getLogger(__name__)

@router.post("/payment/checkout")
async def create_checkout_session(
    user_id: str = Depends(get_current_user),
    session: AsyncSession = Depends(get_session)
):
    # Get user email
    user = await session.get(User, user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    try:
        # For extension, success/cancel URL might need to be a generic page or the extension itself (tricky)
        # Usually we redirect to a success page on our LP/Website.
        # For now, let's assume we have a simple success page.
        success_url = "https://example.com/success"
        cancel_url = "https://example.com/cancel"
        
        url = stripe_service.create_checkout_session(
            user_id=user_id,
            email=user.email,
            success_url=success_url,
            cancel_url=cancel_url
        )
        return {"checkout_url": url}
    except Exception as e:
        logger.error(f"Stripe checkout error: {e}")
        raise HTTPException(status_code=500, detail="Failed to create checkout session")

@router.post("/payment/webhook")
async def stripe_webhook(request: Request, stripe_signature: str = Header(None), session: AsyncSession = Depends(get_session)):
    payload = await request.body()
    
    try:
        event = stripe_service.construct_event(payload, stripe_signature)
    except ValueError as e:
        raise HTTPException(status_code=400, detail="Invalid payload")
    except Exception as e:
        raise HTTPException(status_code=400, detail="Invalid signature")

    if event['type'] == 'checkout.session.completed':
        session_data = event['data']['object']
        user_id = session_data.get('client_reference_id')
        
        if user_id:
            logger.info(f"Payment successful for user {user_id}")
            user = await session.get(User, user_id)
            if user:
                user.is_pro = True
                session.add(user)
                await session.commit()
            else:
                logger.error(f"User {user_id} not found during webhook processing")

    return {"status": "success"}
