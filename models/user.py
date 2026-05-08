# models/user.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class RoleEnum(str, Enum):
    citizen = "citizen"
    staff = "staff"
    admin = "admin"

class UserUpdate(BaseModel):
    full_name: Optional[str] = None

class UserPromote(BaseModel):
    user_id: str
    role: RoleEnum
    department_id: Optional[str] = None
