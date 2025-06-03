# notification_service.py
import os
import httpx

FIREBASE_SERVER_KEY = os.getenv("FIREBASE_SERVER_KEY")  # securely stored env var

async def send_fcm_notification(token: str, title: str, body: str, data: dict = None):
    headers = {
        "Authorization": f"key={FIREBASE_SERVER_KEY}",
        "Content-Type": "application/json"
    }
    payload = {
        "to": token,
        "notification": {
            "title": title,
            "body": body,
        },
        "data": {
            "click_action": "FLUTTER_NOTIFICATION_CLICK",
        }
    }
    if data:
        payload["data"].update(data)

    async with httpx.AsyncClient() as client:
        response = await client.post("https://fcm.googleapis.com/fcm/send", headers=headers, json=payload)
        if response.status_code != 200:
            raise Exception(f"FCM Failed: {response.text}")
