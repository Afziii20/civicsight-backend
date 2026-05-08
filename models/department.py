# models/department.py
from pydantic import BaseModel
from typing import Optional, List

class DepartmentCreate(BaseModel):
    name: str
    email: str
    category_tags: Optional[List[str]] = []
