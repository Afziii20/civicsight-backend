# auth.py
from fastapi import Header, HTTPException, Depends
from supabase import create_client
from config import SUPABASE_URL, SUPABASE_SERVICE_KEY

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]

    try:
        client = create_client(SUPABASE_URL, SUPABASE_SERVICE_KEY)
        user = client.auth.get_user(token)
        if not user or not user.user:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user.user
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Could not validate token: {str(e)}")

def get_optional_user(authorization: str = Header(default=None)):
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None
