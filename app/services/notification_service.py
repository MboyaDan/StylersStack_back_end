from firebase_admin import messaging
import logging
from typing import Optional

logger = logging.getLogger(__name__)

def send_fcm_notification(token: str, title: str, body: str, data: Optional[dict] = None):
    """
    Sends FCM notification using Firebase Admin SDK (HTTP v1 API).
    """
    message = messaging.Message(
        notification=messaging.Notification(
            title=title,
            body=body
        ),
        token=token,
        data=data or {
            "click_action": "FLUTTER_NOTIFICATION_CLICK"
        }
    )

    try:
        response = messaging.send(message)
        logger.info(f"FCM notification sent successfully: {response}")
        return {"message_id": response}
    except Exception as e:
        logger.exception(f"Failed to send FCM notification: {e}")
        raise Exception("FCM send failed")
