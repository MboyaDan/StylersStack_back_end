#verify token on each request using Firebase’s public keys.
import firebase_admin
from firebase_admin import auth, credentials
from fastapi import HTTPException, Request

# Initialize Firebase Admin SDK only once using the service account credentials
try:
    if not firebase_admin._apps:
        cred = credentials.Certificate("firebase_admin_sdk.json") 
        firebase_admin.initialize_app(cred)
except Exception as e:
    raise RuntimeError(f"Failed to initialize Firebase Admin SDK: {e}")
def extract_firebase_token(request: Request):
    """
    Extracts the Firebase ID token from the Authorization header of the request.

    Returns:
        str: The Firebase ID token.
    
    Raises:
        HTTPException: If the token is missing or malformed.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    return auth_header.split("Bearer ")[1]
def verify_firebase_token(request: Request):
    """
    Verifies the Firebase ID token from the Authorization header of the request.

    Returns:
        decoded_token (dict): Contains Firebase user info such as UID, email, etc.
    
    Raises:
        HTTPException: If token is missing, malformed, or invalid.
    """
    auth_header = request.headers.get("Authorization")

    if not auth_header or not auth_header.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid or missing token")

    token = auth_header.split("Bearer ")[1]

    try:
        decoded_token = auth.verify_id_token(token)
        return decoded_token
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Token verification failed: {str(e)}")
