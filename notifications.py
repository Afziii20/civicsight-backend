# notifications.py

import resend
import os
from dotenv import load_dotenv

load_dotenv()

resend.api_key = os.getenv("RESEND_API_KEY")

def send_report_assigned(department_email: str, department_name: str,
                          report_id: str, category: str,
                          priority: str, description: str):
    """Notify department that a new report has been assigned to them."""
    resend.Emails.send({
        "from": "CivicSight <onboarding@resend.dev>",
        "to": department_email,
        "subject": f"[{priority.upper()}] New {category.replace('_', ' ').title()} Report Assigned",
        "html": f"""
        <h2>New Report Assigned to {department_name}</h2>
        <table style="border-collapse:collapse; width:100%">
            <tr><td><b>Report ID</b></td><td>{report_id}</td></tr>
            <tr><td><b>Category</b></td><td>{category.replace('_', ' ').title()}</td></tr>
            <tr><td><b>Priority</b></td><td>{priority.upper()}</td></tr>
            <tr><td><b>Description</b></td><td>{description}</td></tr>
        </table>
        <br>
        <a href="http://localhost:3000/reports/{report_id}"
           style="background:#2563eb;color:white;padding:10px 20px;
                  border-radius:5px;text-decoration:none">
            View Report
        </a>
        """
    })


def send_report_resolved(citizen_email: str, report_id: str,
                          category: str, note: str = ""):
    """Notify citizen their report has been resolved."""
    resend.Emails.send({
        "from": "CivicSight <onboarding@resend.dev>",
        "to": citizen_email,
        "subject": f"Your report has been resolved ✓",
        "html": f"""
        <h2>Your Report Has Been Resolved</h2>
        <p>Good news! The {category.replace('_', ' ')} issue you reported
           has been marked as resolved by our team.</p>
        {"<p><b>Note from staff:</b> " + note + "</p>" if note else ""}
        <br>
        <a href="http://localhost:3000/reports/{report_id}"
           style="background:#16a34a;color:white;padding:10px 20px;
                  border-radius:5px;text-decoration:none">
            View Report
        </a>
        """
    })


def send_escalation_alert(admin_email: str, report_id: str,
                           category: str, reason: str = ""):
    """Alert admin when a report is escalated."""
    resend.Emails.send({
        "from": "CivicSight <onboarding@resend.dev>",
        "to": admin_email,
        "subject": f"⚠️ Report Escalated — Immediate Attention Required",
        "html": f"""
        <h2>Report Escalated</h2>
        <p>A report has been escalated and requires your attention.</p>
        <table style="border-collapse:collapse; width:100%">
            <tr><td><b>Report ID</b></td><td>{report_id}</td></tr>
            <tr><td><b>Category</b></td><td>{category.replace('_', ' ').title()}</td></tr>
            <tr><td><b>Reason</b></td><td>{reason or "Not specified"}</td></tr>
        </table>
        <br>
        <a href="http://localhost:3000/reports/{report_id}"
           style="background:#dc2626;color:white;padding:10px 20px;
                  border-radius:5px;text-decoration:none">
            Review Now
        </a>
        """
    })
