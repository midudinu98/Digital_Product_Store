import stripe

from fastapi import APIRouter,Depends,HTTPException,Request
from sqlalchemy.orm import session

from app.core.config import settings
from app.core.database import get_db
from app.models import Order, Payment
from app.router.auth import get_current_user


stripe.api_key = settings.STRIPE_SECRET_KEY


router = APIRouter(prefix="/payments",tags=["Payments"])


# Create Stripe Checkout Session
@router.post("/create-checkout-session")
def create_checkout_session(order_id: int,db: session = Depends(get_db),current_user=Depends(get_current_user)):
    # Find user's order
    order = db.query(Order).filter(Order.id == order_id,Order.user_id == current_user.id).first()

    if not order:
        raise HTTPException(status_code=404,detail="Order not found")

    if order.status != "PENDING":
        raise HTTPException(status_code=400,detail="Order is not pending")

    # Get payment
    payment = db.query(Payment).filter(Payment.order_id == order.id).first()

    if not payment:
        raise HTTPException(status_code=404,detail="Payment record not found")

    try:
        checkout_session = stripe.checkout.Session.create(
            payment_method_types=["card"],
            line_items=[
                {
                    "price_data": {
                        "currency": "inr",
                        "product_data": {
                            "name": f"Order #{order.id}"
                        },
                        "unit_amount": int(
                            order.total_amount * 100
                        ),
                    },
                    "quantity": 1,
                }
            ],
            mode="payment",
            success_url="http://localhost:3000/payment-success",
            cancel_url="http://localhost:3000/payment-cancelled",
            metadata={
                "order_id": str(order.id)
            }
        )

        payment.stripe_session_id = checkout_session.id

        db.commit()

        return {
            "checkout_url": checkout_session.url,
            "session_id": checkout_session.id,
            "order_id": order.id
        }

    except stripe.StripeError as e:
        raise HTTPException(status_code=400,detail=str(e))


# Stripe Webhook
@router.post("/webhook")
async def stripe_webhook(request: Request,db: session = Depends(get_db)):
    payload = await request.body()
    signature = request.headers.get("stripe-signature")

    if not signature:
        raise HTTPException(status_code=400,detail="Missing Stripe signature")

    try:
        event = stripe.Webhook.construct_event(payload,signature,settings.STRIPE_WEBHOOK_SECRET)

    except ValueError:
        raise HTTPException(status_code=400,detail="Invalid webhook payload")

    except stripe.SignatureVerificationError:
        raise HTTPException(status_code=400,detail="Invalid webhook signature")

    # Payment successful
    if event["type"] == "checkout.session.completed":

        session = event["data"]["object"]

        order_id = session["metadata"].get("order_id")

        if order_id:
            order = db.query(Order).filter( Order.id == int(order_id)).first()

            payment = db.query(Payment).filter(Payment.order_id == int(order_id)).first()

            if order:
                order.status = "PAID"

            if payment:
                payment.status = "PAID"
                payment.stripe_session_id = session["id"]

                payment_intent = session.get("payment_intent")

                if payment_intent:
                    payment.stripe_payment_intent_id = (payment_intent)

            db.commit()

    return {"message": "Webhook received"}