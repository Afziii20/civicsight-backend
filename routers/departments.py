# routers/departments.py
from fastapi import APIRouter, Depends
from database import get_supabase
from auth import get_current_user

router = APIRouter(prefix="/departments", tags=["departments"])

@router.get("/")
def list_departments(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    result = supabase.table("departments").select("*").execute()
    return result.data
