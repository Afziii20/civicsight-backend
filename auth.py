# auth.py
import os
import httpx
from fastapi import Header, HTTPException
from dotenv import load_dotenv

load_dotenv()

SUPABASE_URL = os.getenv("SUPABASE_URL")
SUPABASE_SERVICE_KEY = os.getenv("SUPABASE_SERVICE_KEY")

def get_current_user(authorization: str = Header(...)):
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid auth header")

    token = authorization.split(" ")[1]

    # Debug — remove after fixing
    if not SUPABASE_URL or not SUPABASE_SERVICE_KEY:
        raise HTTPException(
            status_code=500,
            detail=f"Missing env vars: URL={'set' if SUPABASE_URL else 'MISSING'}, KEY={'set' if SUPABASE_SERVICE_KEY else 'MISSING'}"
        )

    try:
        response = httpx.get(
            f"{SUPABASE_URL}/auth/v1/user",
            headers={
                "Authorization": f"Bearer {token}",
                "apikey": SUPABASE_SERVICE_KEY,
            },
            timeout=10,
        )
        if response.status_code != 200:
            raise HTTPException(status_code=401, detail="Invalid or expired token")

        user_data = response.json()

        class User:
            def __init__(self, data):
                self.id = data["id"]
                self.email = data.get("email", "")

        return User(user_data)

    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=401, detail=f"Auth error: {str(e)}")

def get_optional_user(authorization: str = Header(default=None)):
    if not authorization:
        return None
    try:
        return get_current_user(authorization)
    except HTTPException:
        return None
