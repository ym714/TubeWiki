import stripe
from core.config import config

stripe.api_key = config.STRIPE_SECRET_KEY

class StripeService:
    def create_checkout_session(self, user_id: str, email: str, success_url: str, cancel_url: str):
        try:
            checkout_session = stripe.checkout.Session.create(
                payment_method_types=['card'],
                line_items=[
                    {
                        'price': config.STRIPE_PRICE_ID,
                        'quantity': 1,
                    },
                ],
                mode='subscription',
                success_url=success_url,
                cancel_url=cancel_url,
                client_reference_id=user_id,
                customer_email=email,
                metadata={
                    "user_id": user_id
                }
            )
            return checkout_session.url
        except Exception as e:
            print(f"Error creating checkout session: {e}")
            raise e

    def construct_event(self, payload, sig_header):
        return stripe.Webhook.construct_event(
            payload, sig_header, config.STRIPE_WEBHOOK_SECRET
        )

stripe_service = StripeService()
