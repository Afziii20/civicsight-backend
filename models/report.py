# models/report.py
from pydantic import BaseModel
from typing import Optional
from enum import Enum

class PriorityEnum(str, Enum):
    critical = "critical"
    high = "high"
    medium = "medium"
    low = "low"

class StatusEnum(str, Enum):
    submitted = "submitted"
    ai_processing = "ai_processing"
    needs_review = "needs_review"
    assigned = "assigned"
    in_progress = "in_progress"
    escalated = "escalated"
    resolved = "resolved"
    rejected = "rejected"

class ReportCreate(BaseModel):
    citizen_description: Optional[str] = None
    lat: Optional[float] = None
    lng: Optional[float] = None
    address: Optional[str] = None
    image_url: str

class ReportStatusUpdate(BaseModel):
    new_status: StatusEnum
    note: Optional[str] = None

class ReportManualClassify(BaseModel):
    category: str
    priority: PriorityEnum
    note: Optional[str] = None
