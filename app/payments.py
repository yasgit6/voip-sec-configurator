from fastapi import HTTPException
import stripe
# stripe.api_key = "your_secret_key"

def create_checkout_session(price_id: str, customer_email: str):
    try:
        session = stripe.checkout.Session.create(
            payment_method_types=['card'],
            line_items=[{
                'price': price_id,  # 'price_abc123' from Stripe dashboard
                'quantity': 1,
            }],
            mode='payment',
            success_url='https://yourdomain.com/success',
            cancel_url='https://yourdomain.com/cancel',
            customer_email=customer_email,
        )
        return session
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
