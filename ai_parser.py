import os
import json
import google.generativeai as genai

API_KEY = os.getenv("GEMINI_API_KEY")
if API_KEY:
    genai.configure(api_key=API_KEY)

def extract_mission_telemetry(raw_notes: str) -> dict:
    prompt = f"""
    You are an Aviation Regulatory Safety Inspector.
    Extract key flight parameters from this pilot's mission submission:
    "{raw_notes}"

    Return ONLY raw JSON with these exact keys:
    {{
      "mtow_kg": float (mass in kg; default 1.8 if unspecified),
      "planned_altitude_m": float (planned altitude in meters. Convert ft to meters if needed. Default 45.0),
      "over_uninvolved_people": boolean (true if urban public spaces/crowds/pedestrians mentioned),
      "visual_line_of_sight": boolean (true if VLOS, false if BVLOS or long distance beyond view),
      "controlled_airspace_proximity": boolean (true if near airport, aerodrome, military zone, or helipad),
      "summary_log": "15-word technical summary of flight intent"
    }}
    """
    if API_KEY:
        try:
            model = genai.GenerativeModel("gemini-1.5-pro")
            response = model.generate_content(prompt)
            clean_json = response.text.strip().replace("```json", "").replace("```", "")
            return json.loads(clean_json)
        except Exception as e:
            print(f"[AI Extraction Fallback Triggered]: {e}")

    low = raw_notes.lower()
    return {
        "mtow_kg": 5.5 if any(k in low for k in ["heavy", "matrice", "payload", "hexacopter", "lidar"]) else 1.2,
        "planned_altitude_m": 165.0 if any(k in low for k in ["165m", "high altitude", "540ft", "antenna"]) else 50.0,
        "over_uninvolved_people": any(k in low for k in ["crowd", "people", "pedestrian", "bystanders", "street", "road"]),
        "visual_line_of_sight": not any(k in low for k in ["bvlos", "beyond visual", "out of sight"]),
        "controlled_airspace_proximity": any(k in low for k in ["airport", "runway", "helipad", "ctr", "frz"]),
        "summary_log": raw_notes[:100]
    }