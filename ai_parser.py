import os
import json
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def extract_mission_telemetry(raw_notes: str) -> dict:
    prompt = f"""
    You are an Aviation Regulatory Safety Inspector for UK CAA / JARUS SORA.
    Extract key flight telemetry from this remote pilot's operational plan:
    "{raw_notes}"

    Return ONLY raw JSON with these exact keys:
    {{
      "mtow_kg": float (mass in kg; default 1.8 if unspecified),
      "planned_altitude_m": float (planned altitude in meters. Convert feet to meters by dividing by 3.28 if specified in ft. Default 45.0),
      "over_uninvolved_people": boolean (true if urban streets, pedestrians, crowds, or events are mentioned),
      "visual_line_of_sight": boolean (true if VLOS, false if BVLOS or beyond visual range),
      "controlled_airspace_proximity": boolean (true if near aerodrome, CTR, FRZ, runway, or airfield),
      "summary_log": "one-sentence concise technical synopsis of planned operation"
    }}
    """
    if API_KEY:
        # Try current supported model identifiers
        for model_id in ["gemini-1.5-flash", "gemini-1.5-pro-latest", "gemini-pro"]:
            try:
                model = genai.GenerativeModel(model_id)
                response = model.generate_content(prompt)
                clean_json = response.text.strip().replace("```json", "").replace("```", "")
                return json.loads(clean_json)
            except Exception as e:
                continue

    # Deterministic aerospace heuristic fallback
    low = raw_notes.lower()
    return {
        "mtow_kg": 5.5 if any(k in low for k in ["heavy", "matrice", "payload", "hexacopter", "lidar", "5.5"]) else 1.5,
        "planned_altitude_m": 165.0 if any(k in low for k in ["165m", "165", "540ft", "mast", "antenna", "high altitude"]) else 45.0,
        "over_uninvolved_people": any(k in low for k in ["crowd", "people", "pedestrian", "bystanders", "street", "road", "assembly"]),
        "visual_line_of_sight": not any(k in low for k in ["bvlos", "beyond visual", "out of sight"]),
        "controlled_airspace_proximity": any(k in low for k in ["airport", "runway", "helipad", "ctr", "frz", "aerodrome"]),
        "summary_log": raw_notes[:120]
    }