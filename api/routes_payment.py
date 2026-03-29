"""
Mirage Studios — Routes Paiement Stripe
Endpoints pour les paiements sécurisés.
"""

from flask import Blueprint, request, jsonify
from flask_cors import cross_origin
import os
import stripe

payment_bp = Blueprint('payment', __name__, url_prefix='/api/payment')

# Prix des services en centimes
PRICES = {
    "pub_15s": {"amount": 29900, "label": "Vidéo Publicitaire 15s"},
    "pub_30s": {"amount": 49900, "label": "Vidéo Publicitaire 30s"},
    "pub_60s": {"amount": 79900, "label": "Vidéo Publicitaire 60s"},
    "court_metrage": {"amount": 99000, "label": "Court Métrage"},
    "long_metrage": {"amount": 490000, "label": "Long Métrage"},
    "scenario": {"amount": 19900, "label": "Scénario IA"},
    "avatar": {"amount": 4900, "label": "Avatar Parlant"},
    "casting": {"amount": 9900, "label": "Casting IA Complet"},
}


def get_stripe():
    secret_key = os.environ.get("STRIPE_SECRET_KEY", "")
    if not secret_key:
        return None
    stripe.api_key = secret_key
    return stripe


@payment_bp.route('/status', methods=['GET'])
@cross_origin()
def payment_status():
    secret_key = os.environ.get("STRIPE_SECRET_KEY", "")
    public_key = os.environ.get("STRIPE_PUBLIC_KEY", "")
    configured = bool(secret_key and public_key)
    return jsonify({
        "configured": configured,
        "status": "ready" if configured else "missing_keys",
        "public_key": public_key if configured else "",
        "currency": "eur",
        "services": len(PRICES),
    })


@payment_bp.route('/prices', methods=['GET'])
@cross_origin()
def list_prices():
    return jsonify({
        "prices": [
            {
                "id": k,
                "label": v["label"],
                "amount_cents": v["amount"],
                "amount_eur": v["amount"] / 100,
                "display": f"{v['amount'] / 100:.0f}€"
            }
            for k, v in PRICES.items()
        ]
    })


@payment_bp.route('/create-intent', methods=['POST', 'OPTIONS'])
@cross_origin()
def create_payment_intent():
    if request.method == 'OPTIONS':
        return jsonify({}), 200

    data = request.get_json()
    if not data or 'service_id' not in data:
        return jsonify({"error": "service_id requis"}), 400

    service_id = data['service_id']
    if service_id not in PRICES:
        return jsonify({"error": f"Service inconnu : {service_id}"}), 400

    s = get_stripe()
    if not s:
        return jsonify({
            "demo": True,
            "client_secret": "demo_secret_123",
            "amount": PRICES[service_id]["amount"],
            "label": PRICES[service_id]["label"],
            "message": "Mode demo - cles Stripe requises"
        })

    try:
        intent = s.PaymentIntent.create(
            amount=PRICES[service_id]["amount"],
            currency="eur",
            metadata={
                "service": service_id,
                "client_name": data.get("client_name", ""),
                "client_email": data.get("client_email", ""),
                "project_description": data.get("description", ""),
            }
        )
        return jsonify({
            "success": True,
            "client_secret": intent.client_secret,
            "payment_intent_id": intent.id,
            "amount": PRICES[service_id]["amount"],
            "amount_eur": PRICES[service_id]["amount"] / 100,
            "label": PRICES[service_id]["label"],
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_bp.route('/confirm/<payment_intent_id>', methods=['GET'])
@cross_origin()
def confirm_payment(payment_intent_id):
    if payment_intent_id.startswith("demo_"):
        return jsonify({
            "status": "succeeded",
            "demo": True,
            "message": "Paiement demo confirme !"
        })

    s = get_stripe()
    if not s:
        return jsonify({"error": "Stripe non configure"}), 500

    try:
        intent = s.PaymentIntent.retrieve(payment_intent_id)
        return jsonify({
            "status": intent.status,
            "amount_eur": intent.amount / 100,
            "service": intent.metadata.get("service"),
            "client_email": intent.metadata.get("client_email"),
        })
    except Exception as e:
        return jsonify({"error": str(e)}), 500


@payment_bp.route('/webhook', methods=['POST'])
def stripe_webhook():
    payload = request.get_data()
    sig_header = request.headers.get('Stripe-Signature')
    webhook_secret = os.environ.get("STRIPE_WEBHOOK_SECRET", "")

    try:
        if webhook_secret:
            event = stripe.Webhook.construct_event(payload, sig_header, webhook_secret)
        else:
            event = {"type": "payment_intent.succeeded", "data": {}}

        if event["type"] == "payment_intent.succeeded":
            print(f"[Stripe] Paiement recu !")

        return jsonify({"status": "ok"})
    except Exception as e:
        return jsonify({"error": str(e)}), 400