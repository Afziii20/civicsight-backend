# router.py

from supabase import Client

# Fallback map (used if DB lookup fails)
CATEGORY_MAP = {
    "pothole":            "Roads & Infrastructure",
    "road_damage":        "Roads & Infrastructure",
    "broken_streetlight": "Electrical",
    "garbage":            "Sanitation",
    "illegal_dumping":    "Sanitation",
    "water_leak":         "Water & Sewage",
    "flooding":           "Water & Sewage",
    "park_damage":        "Parks & Public Spaces",
    "graffiti":           "Parks & Public Spaces",
    "noise":              "General Administration",
    "other":              "General Administration",
}

def get_department_for_category(supabase: Client, category: str) -> dict | None:
    """
    Looks up the department_id for a given AI category.
    Returns the department row or None if not found.
    """
    result = (
        supabase
        .table("category_department_map")
        .select("department_id, departments(id, name, email)")
        .eq("category", category)
        .single()
        .execute()
    )
    return result.data if result.data else None

def route_report(supabase: Client, report_id: str, category: str) -> dict:
    """
    Given a report ID and AI category:
    1. Finds the right department
    2. Updates the report's assigned_department_id
    3. Returns routing result
    """
    dept = get_department_for_category(supabase, category)

    if not dept:
        # Fallback: route to General Administration
        fallback = (
            supabase
            .table("departments")
            .select("id, name, email")
            .eq("name", "General Administration")
            .single()
            .execute()
        )
        dept = {"department_id": fallback.data["id"], "departments": fallback.data}

    dept_id = dept["department_id"]

    # Update the report
    supabase.table("reports").update({
        "assigned_department_id": dept_id,
        "status": "assigned",
    }).eq("id", report_id).execute()

    return {
        "report_id": report_id,
        "assigned_to": dept["departments"]["name"],
        "department_id": dept_id,
        "department_email": dept["departments"]["email"],
    }
