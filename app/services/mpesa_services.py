import base64
import requests
import os
import logging
from datetime import datetime
from typing import Optional, Dict, Any
from requests.exceptions import RequestException

# M-Pesa API integration for payment processing
def get_access_token() -> Optional[str]:
    try:
        consumer_key = os.getenv("MPESA_CONSUMER_KEY")
        consumer_secret = os.getenv("MPESA_CONSUMER_SECRET")
        if not consumer_key or not consumer_secret:
            raise ValueError("Missing M-Pesa API credentials in environment variables")

        credentials = base64.b64encode(f"{consumer_key}:{consumer_secret}".encode()).decode()
        headers = {"Authorization": f"Basic {credentials}"}

        response = requests.get(
            "https://sandbox.safaricom.co.ke/oauth/v1/generate?grant_type=client_credentials",
            headers=headers,
            timeout=10
        )

        print(f"MPESA consumer_key: {consumer_key}")
        print(f"MPESA consumer_secret: {consumer_secret}")
        print(f"Authorization header: Basic {credentials}")


        if response.status_code != 200:
            logging.error(f"[M-Pesa Auth] Failed to get token: {response.status_code} - {response.text}")
            return None

        token = response.json().get("access_token")
        if not token:
            logging.error("[M-Pesa Auth] Access token missing in response")
            return None

        logging.info("[M-Pesa Auth] Access token obtained successfully")
        return token

    except RequestException as e:
        logging.exception("[M-Pesa Auth] Network error while fetching access token")
        return None
    except Exception as e:
        logging.exception(f"[M-Pesa Auth] Unexpected error: {e}")
        return None
#intiate payment with M-Pesa API

def initiate_mpesa_payment(payment) -> Dict[str, Any]:
    try:
        access_token = get_access_token()
        if not access_token:
            return {"error": "Authentication with M-Pesa API failed"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        business_short_code = os.getenv("MPESA_SHORTCODE")
        passkey = os.getenv("MPESA_PASSKEY")
        callback_url = os.getenv("MPESA_CALLBACK_URL")

        if not all([business_short_code, passkey, callback_url]):
            logging.error("[M-Pesa Config] Missing one or more required environment variables")
            return {"error": "M-Pesa configuration incomplete"}

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
            "CallBackURL": callback_url,
            "AccountReference": payment.order_id,
            "TransactionDesc": "Order Payment"
        }
        #loging the phone number used for payment
        logging.info(f"Full M-Pesa STK payload: {payload}")


        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpush/v1/processrequest",
            headers=headers,
            json=payload,
            timeout=15
        )

        response_data = response.json()

        if response.status_code != 200 or "errorMessage" in response_data:
            logging.error(f"[M-Pesa STK Push] Failed with status {response.status_code}: {response_data}")
            return {
                "error": "Failed to initiate M-Pesa payment",
                "status_code": response.status_code,
                "details": response_data
            }

        logging.info(f"[M-Pesa STK Push] Success for order {payment.order_id}: {response_data}")
        return response_data

    except RequestException as e:
        logging.exception("[M-Pesa STK Push] Network-related exception")
        return {"error": "Network error during payment initiation"}
    except Exception as e:
        logging.exception(f"[M-Pesa STK Push] Unexpected error: {e}")
        return {"error": "Unexpected error during M-Pesa payment"}

# Query M-Pesa payment status using CheckoutRequestID
def query_mpesa_payment_status(checkout_request_id: str) -> Dict[str, Any]:
    try:
        access_token = get_access_token()
        if not access_token:
            return {"error": "Authentication with M-Pesa API failed"}

        timestamp = datetime.now().strftime('%Y%m%d%H%M%S')
        business_short_code = os.getenv("MPESA_SHORTCODE")
        passkey = os.getenv("MPESA_PASSKEY")

        if not all([business_short_code, passkey]):
            logging.error("[M-Pesa Config] Missing shortcode or passkey for query")
            return {"error": "M-Pesa configuration incomplete for status query"}

        password = base64.b64encode(f"{business_short_code}{passkey}{timestamp}".encode()).decode()

        payload = {
            "BusinessShortCode": business_short_code,
            "Password": password,
            "Timestamp": timestamp,
            "CheckoutRequestID": checkout_request_id
        }

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }

        response = requests.post(
            "https://sandbox.safaricom.co.ke/mpesa/stkpushquery/v1/query",
            headers=headers,
            json=payload,
            timeout=15
        )

        response_data = response.json()

        if response.status_code != 200 or "errorMessage" in response_data:
            logging.error(f"[M-Pesa STK Query] Failed with status {response.status_code}: {response_data}")
            return {
                "error": "Failed to query M-Pesa payment status",
                "status_code": response.status_code,
                "details": response_data
            }

        logging.info(f"[M-Pesa STK Query] Status check: {response_data}")
        return response_data

    except RequestException as e:
        logging.exception("[M-Pesa STK Query] Network-related exception")
        return {"error": "Network error during status query"}
    except Exception as e:
        logging.exception(f"[M-Pesa STK Query] Unexpected error: {e}")
        return {"error": "Unexpected error during payment status query"}
