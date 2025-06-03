import base64, requests, os
from datetime import datetime

def get_access_token():
    consumer_key = os.getenv("MPESA_CONSUMER_KEY")
    consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
    credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()

    headers = {"Authorization": f"Basic {credentials}"}
    response = requests.get("https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials", headers=headers)
    return response.json().get("access_token")

def initiate_mpesa_payment(payment):
    access_token = get_access_token()
    timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
    business_short_code = os.getenv("MPESA_SHORTCODE")
    passkey = os.getenv("MPESA_PASSKEY")
    password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()

    payload = {
        "BusinessShortCode": business_short_code,
        "Password": password,
        "Timestamp": timestamp,
        "TransactionType": "CustomerPayBillOnline",
        "Amount": int(payment.amount),
        "PartyA": payment.phone_number,
        "PartyB": business_short_code,
        "PhoneNumber": payment.phone_number,
        "CallBackURL": os.getenv("MPESA_CALLBACK_URL"),
        "AccountReference": payment.order_id,
        "TransactionDesc": "Order Payment"
    }

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest", headers=headers, json=payload)
    return response.json()
