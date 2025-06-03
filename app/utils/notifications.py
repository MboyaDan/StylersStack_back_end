from app.services.notification_service import send_fcm_notification

def send_fcm_notification(token: str, title: str, body: str):
    # You can extend this later with retries, logging, etc.
    send_fcm_notification(token=token, title=title, body=body)
