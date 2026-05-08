# routers/admin.py
from fastapi import APIRouter, Depends, HTTPException
from database import get_supabase
from auth import get_current_user
from models.user import UserPromote
from models.department import DepartmentCreate

router = APIRouter(prefix="/admin", tags=["admin"])

def require_admin(current_user=Depends(get_current_user)):
    supabase = get_supabase()
    user = supabase.table("users").select("role").eq("id", current_user.id).single().execute()
    if not user.data or user.data["role"] != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user

@router.post("/promote")
def promote_user(body: UserPromote, current_user=Depends(require_admin)):
    supabase = get_supabase()
    supabase.table("users").update({
        "role": body.role,
        "department_id": body.department_id,
    }).eq("id", body.user_id).execute()
    return {"message": f"User promoted to {body.role}"}

@router.get("/reviews")
def get_pending_reviews(current_user=Depends(require_admin)):
    supabase = get_supabase()
    result = supabase.table("reports").select("*").eq("needs_human_review", True).execute()
    return result.data

@router.post("/departments")
def create_department(body: DepartmentCreate, current_user=Depends(require_admin)):
    supabase = get_supabase()
    result = supabase.table("departments").insert({
        "name": body.name,
        "email": body.email,
        "category_tags": body.category_tags,
    }).execute()
    return result.data[0]
