"""
Payment gateway wrapper.
- If STRIPE_SECRET_KEY is set in .env -> real Stripe test mode is used.
- Otherwise a small built-in sandbox gateway is used so everything works offline.
Both return the same shaped dicts so the rest of the code doesn't care.
"""
import hashlib
import hmac
import json
import uuid
from decimal import Decimal

from fastapi import HTTPException

from app.config import settings


class SandboxGateway:
    name = "sandbox"

    def create_intent(self, amount: Decimal, currency: str, idempotency_key: str, metadata: dict):
        ref = "sb_pi_" + uuid.uuid4().hex[:20]
        return {"ref": ref, "client_secret": ref + "_secret_" + uuid.uuid4().hex[:10], "status": "pending"}

    def refund(self, ref: str, amount: Decimal):
        return {"ref": "sb_re_" + uuid.uuid4().hex[:20], "status": "succeeded"}

    @staticmethod
    def sign(body: bytes) -> str:
        return hmac.new(settings.sandbox_webhook_secret.encode(), body, hashlib.sha256).hexdigest()

    def parse_webhook(self, body: bytes, signature: str | None):
        if not signature or not hmac.compare_digest(self.sign(body), signature):
            raise HTTPException(400, "Invalid webhook signature")
        event = json.loads(body)
        # sandbox event looks like {"id": "...", "type": "payment.succeeded", "data": {"ref": "..."}}
        return {
            "id": event["id"],
            "type": event["type"],
            "ref": event["data"]["ref"],
            "reason": event["data"].get("reason"),
            "raw": event,
        }


class StripeGateway:
    name = "stripe"

    def __init__(self):
        import stripe
        stripe.api_key = settings.stripe_secret_key
        self.stripe = stripe

    def create_intent(self, amount, currency, idempotency_key, metadata):
        intent = self.stripe.PaymentIntent.create(
            amount=int(Decimal(amount) * 100),  # stripe wants the smallest unit
            currency=currency.lower(),
            metadata=metadata,
            automatic_payment_methods={"enabled": True},
            idempotency_key=idempotency_key,
        )
        return {"ref": intent.id, "client_secret": intent.client_secret, "status": "pending"}

    def refund(self, ref, amount):
        refund = self.stripe.Refund.create(payment_intent=ref, amount=int(Decimal(amount) * 100))
        status = "succeeded" if refund.status == "succeeded" else "processing"
        return {"ref": refund.id, "status": status}

    def parse_webhook(self, body, signature):
        try:
            event = self.stripe.Webhook.construct_event(body, signature, settings.stripe_webhook_secret)
        except Exception:
            raise HTTPException(400, "Invalid Stripe signature")
        mapping = {
            "payment_intent.succeeded": "payment.succeeded",
            "payment_intent.payment_failed": "payment.failed",
        }
        obj = event["data"]["object"]
        reason = None
        if obj.get("last_payment_error"):
            reason = obj["last_payment_error"].get("message")
        return {"id": event["id"], "type": mapping.get(event["type"], event["type"]),
                "ref": obj.get("id"), "reason": reason, "raw": dict(event)}


class ManualGateway:
    """used for COD refunds - money is returned offline, we only record it"""
    name = "manual"

    def refund(self, ref, amount):
        return {"ref": "manual_" + uuid.uuid4().hex[:16], "status": "succeeded"}


def get_gateway():
    if settings.stripe_secret_key:
        return StripeGateway()
    return SandboxGateway()


def gateway_for(name):
    if name == "cod":
        return ManualGateway()
    if name == "stripe":
        return StripeGateway()
    return SandboxGateway()