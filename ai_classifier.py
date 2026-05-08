# ai_classifier.py
from logger import get_logger
import ollama
import base64
import json
import httpx
import os
from dotenv import load_dotenv
from typing import Optional

logger = get_logger("ai_classifier")

load_dotenv()

SYSTEM_PROMPT = """
You are a municipal issue classifier for a city reporting system.
Given an image and optional citizen description, return ONLY a
JSON object with these fields:

{
  "is_valid_issue": true/false,
  "category": one of [pothole, road_damage, broken_streetlight,
               garbage, illegal_dumping, water_leak, flooding,
               park_damage, graffiti, noise, other],
  "priority": one of [critical, high, medium, low],
  "confidence": float between 0 and 1,
  "ai_description": "2-3 sentence factual description of the issue",
  "priority_reason": "one sentence explaining why this priority"
}

Priority rules:
- critical: immediate safety risk (exposed wires, major flooding, collapsed road)
- high: infrastructure failure affecting many people
- medium: quality of life issue, not immediately dangerous
- low: cosmetic or minor

If the image does not show a real civic issue, set is_valid_issue
to false and category to "other".
Return ONLY the JSON. No explanation. No markdown.
"""

def read_image_base64(image_path: str = None, image_url: str = None) -> str:
    if image_path:
        with open(image_path, "rb") as f:
            return base64.b64encode(f.read()).decode("utf-8")
    else:
        response = httpx.get(image_url, timeout=15, headers={"User-Agent": "CivicSight/1.0"})
        response.raise_for_status()
        return base64.b64encode(response.content).decode("utf-8")

def classify_image(image_url: str = None, image_path: str = None,
                   citizen_description: Optional[str] = None) -> dict:

    user_text = "Classify this civic issue image.\n\n" + SYSTEM_PROMPT
    if citizen_description:
        user_text += f"\n\nCitizen description: {citizen_description}"

    image_b64 = read_image_base64(image_path=image_path, image_url=image_url)

    response = ollama.chat(
        model="moondream",
        messages=[
            {
                "role": "user",
                "content": user_text,
                "images": [image_b64],
            }
        ],
    )

    raw = response["message"]["content"].strip()

    # Strip markdown fences if model slips up
    if raw.startswith("```"):
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

# Strip markdown fences
    if "```" in raw:
        raw = raw.split("```")[1]
        if raw.startswith("json"):
            raw = raw[4:]
        raw = raw.strip()

    # Extract just the JSON object if there's extra text
   # Extract just the JSON object if there's extra text
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]

    # If JSON is truncated (no closing brace), patch it up
    if not raw.strip().endswith("}"):
        # Close any open string then close the object
        raw = raw.rstrip().rstrip(",")
        if not raw.endswith('"'):
            raw += '"'
        raw += "\n}"

    try:
        result = json.loads(raw)
        # Fill in missing fields with safe defaults
        result.setdefault("is_valid_issue", True)
        result.setdefault("category", "other")
        result.setdefault("priority", "medium")
        result.setdefault("confidence", 0.5)
        result.setdefault("ai_description", "Issue detected.")
        result.setdefault("priority_reason", "Assessed by AI.")
        return result
    except json.JSONDecodeError:
        logger.warning(f"JSON parse failed. Raw output: {raw}")
        raise
