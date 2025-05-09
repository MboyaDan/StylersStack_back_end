#Auth,loggin,CORS,errorHandling
from fastapi import Depends, HTTPException, Request
from firebase_admin import auth

def get_current_user(request: Request):
    id_token = request.headers.get("Authorization")
    if not id_token:
        raise HTTPException(status_code=401, detail="Missing token")

    try:
        decoded_token = auth.verify_id_token(id_token.replace("Bearer ", ""))
        return decoded_token
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid token")