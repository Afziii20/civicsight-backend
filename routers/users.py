# routers/users.py
from fastapi import APIRouter, Depends
from database import get_supabase
from auth import get_current_user
from models.user import UserUpdate

router = APIRouter(prefix="/users", tags=["users"])

@router.get("/me")
def get_me(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("users").select("*").eq("id", current_user.id).single().execute()
    return result.data

@router.patch("/me")
def update_me(body: UserUpdate, current_user=Depends(get_current_user)):
    supabase = get_supabase()
    supabase.table("users").update({"full_name": body.full_name}).eq("id", current_user.id).execute()
    return {"message": "Updated"}
