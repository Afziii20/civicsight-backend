# processor.py
from logger import get_logger
from notifications import send_report_assigned
from supabase import Client
from ai_classifier import classify_image
from state_machine import transition, InvalidTransitionError
from router import route_report
from typing import Optional
import datetime

logger = get_logger("processor")

def process_report(supabase: Client, report_id: str) -> dict:
    """
    Full pipeline for a submitted report:
    1. Fetch report from DB
    2. Call AI classifier
    3. Update report with AI results
    4. Route to department OR flag for human review
    5. Log status history
    """

    # 1. Fetch report
    result = supabase.table("reports").select("*").eq("id", report_id).single().execute()
    report = result.data
    if not report:
        raise ValueError(f"Report {report_id} not found")

    image_url = report["image_url"]
    citizen_description = report.get("citizen_description")

    # 2. Transition to ai_processing
    _log_transition(supabase, report_id, report["status"], "ai_processing", note="AI processing started")
    supabase.table("reports").update({"status": "ai_processing"}).eq("id", report_id).execute()

    # 3. Call AI
    ai_result = classify_image(image_url, citizen_description)

    # 4. Handle invalid issue
    if not ai_result.get("is_valid_issue"):
        supabase.table("reports").update({
            "status": "rejected",
            "ai_category": "other",
            "ai_description": ai_result.get("ai_description", "Not a valid civic issue."),
            "ai_confidence": ai_result.get("confidence", 0.0),
            "ai_priority": "low",
        }).eq("id", report_id).execute()
        _log_transition(supabase, report_id, "ai_processing", "rejected", note="AI: not a valid issue")
        return {"status": "rejected", "reason": "not a valid issue"}

    confidence = ai_result.get("confidence", 0.0)
    needs_review = confidence < 0.75

    # 5. Update report with AI fields
    supabase.table("reports").update({
        "ai_category":    ai_result.get("category"),
        "ai_description": ai_result.get("ai_description"),
        "ai_priority":    ai_result.get("priority"),
        "ai_confidence":  confidence,
        "needs_human_review": needs_review,
    }).eq("id", report_id).execute()

    # 6. Route or flag
    if needs_review:
        supabase.table("reports").update({"status": "needs_review"}).eq("id", report_id).execute()
        _log_transition(supabase, report_id, "ai_processing", "needs_review",
                        note=f"Low confidence: {confidence:.2f}")
        return {"status": "needs_review", "confidence": confidence}
    else:
        routing = route_report(supabase, report_id, ai_result["category"])
        _log_transition(supabase, report_id, "ai_processing", "assigned",
                        note=f"Assigned to {routing['assigned_to']}")

        # 🔔 Send email notification to department
        try:
            send_report_assigned(
                department_email=routing["department_email"],
                department_name=routing["assigned_to"],
                report_id=report_id,
                category=ai_result["category"],
                priority=ai_result["priority"],
                description=ai_result.get("ai_description", ""),
            )
        except Exception as e:
            logger.warning(f"Email notification failed for report {report_id}: {e}")

        return {"status": "assigned", "routing": routing}


def _log_transition(supabase: Client, report_id: str, old_status: str,
                    new_status: str, note: str = ""):
    supabase.table("report_status_history").insert({
        "report_id":  report_id,
        "old_status": old_status,
        "new_status": new_status,
        "note":       note,
    }).execute()
