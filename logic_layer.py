def evaluate_airworthiness_risk(telemetry: dict) -> dict:
  mtow = telemetry.get("mtow_kg", 1.8)
  alt = telemetry.get("planned_altitude_m", 45.0)
  crowd = telemetry.get("over_uninvolved_people", False)
  vlos = telemetry.get("visual_line_of_sight", True)
  near_ctr = telemetry.get("controlled_airspace_proximity", False)

  risk_score = 10
  violations = []
  directives = []

  # 1. Statutory Altitude Cap (120 meters / 400 feet AGL)
  if alt > 120.0:
      risk_score += 45
      violations.append(f"Hard Envelope Breach: Flight altitude ({alt:.1f}m) exceeds 120m statutory ceiling.")
      directives.append("Descend flight plan below 120m AGL or submit CAA Form SRG1320 for non-standard flight.")
  else:
      risk_score += int((alt / 120.0) * 12)

  # 2. Airspace Restriction Zone (FRZ / CTR)
  if near_ctr:
      risk_score += 30
      violations.append("Aerodrome Flight Restriction Zone (FRZ) conflict detected.")
      directives.append("Mandatory Air Traffic Control (ATC) coordination & non-standard flight authorization required.")

  # 3. Visual Line of Sight Boundary
  if not vlos:
      risk_score += 35
      violations.append("BVLOS operation planned without approved detect-and-avoid (DAA) telemetry.")
      directives.append("Restrain to Visual Line of Sight (VLOS) or establish certified airspace segregation.")

  # 4. Ground Risk Class (Kinetic Energy & Human Proximity)
  if crowd:
      if mtow >= 4.0:
          risk_score += 40
          violations.append(f"Severe kinetic hazard: {mtow}kg airframe operated directly over uninvolved assemblies.")
          directives.append("Mandate 50-meter safety cordon and deploy certified parachute recovery mechanism.")
      elif mtow >= 0.9:
          risk_score += 20
          directives.append("Maintain 30-meter A2 Subcategory standoff distance; pilot must hold A2 CofC.")
      else:
          risk_score += 10
          directives.append("Ensure pilot is registered; keep overflight of open-air crowds to minimum duration.")
  else:
      risk_score += 5

  final_score = min(risk_score, 100)

  # Operational Categorization
  if final_score >= 70 or not vlos or near_ctr or alt > 120.0:
      op_category = "SPECIFIC CATEGORY (High Risk)"
      decision = "MISSION REJECTED - SORA AUTHORISATION REQUIRED"
      directives.append("Prepare formal Specific Operations Risk Assessment (SORA) for National Aviation Authority sign-off.")
  elif final_score >= 40:
      op_category = "OPEN CATEGORY A2 (Moderate Risk)"
      decision = "CONDITIONAL APPROVAL - STANDOFF REQUIRED"
      directives.append("Pilot must verify A2 Certificate of Competence (CofC) and check local NOTAMs.")
  else:
      op_category = "OPEN CATEGORY A1 / A3 (Standard Flight)"
      decision = "FLIGHT AUTHORIZED"
      directives.append("Standard pre-flight walkaround: inspect propellers, calibrate IMU, and verify battery cell delta < 0.03V.")

  return {
      "risk_index": final_score,
      "operational_category": op_category,
      "flight_decision": decision,
      "violations": violations,
      "directives": directives
  }