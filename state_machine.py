# state_machine.py

from typing import Optional

VALID_TRANSITIONS = {
    "submitted":     ["ai_processing"],
    "ai_processing": ["assigned", "needs_review"],
    "needs_review":  ["assigned"],
    "assigned":      ["in_progress", "rejected"],
    "in_progress":   ["resolved", "escalated"],
    "escalated":     ["in_progress"],
}

class InvalidTransitionError(Exception):
    pass

def can_transition(current: str, next_status: str) -> bool:
    return next_status in VALID_TRANSITIONS.get(current, [])

def transition(current: str, next_status: str, note: Optional[str] = None) -> dict:
    if not can_transition(current, next_status):
        raise InvalidTransitionError(
            f"Cannot transition from '{current}' to '{next_status}'"
        )
    return {
        "old_status": current,
        "new_status": next_status,
        "note": note,
    }
