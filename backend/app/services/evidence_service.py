from typing import Dict, Any, List, Optional, Tuple

def evaluate_evidence(
    lat: float,
    lon: float,
    nearest_facility: Optional[Dict[str, Any]],
    distance_to_facility_m: float,
    inside_industrial_zone: bool,
    landcover: str,
    temporal_summary: Dict[str, Any],
    frp: Optional[float] = None,
    daynight: Optional[str] = None
) -> Dict[str, Any]:
    """
    Evaluate empirical spatial, temporal, and industrial evidence for thermal events in Giaspura.
    Enforces scientific integrity:
    - Never fabricates ground truth.
    - Never claims proximity proves causation.
    - Indicates classification_method = 'evidence_based' (since supervised ML weights are absent).
    """
    evidence_claims: List[str] = []
    risk_score = 10.0  # Baseline thermal presence score
    classification = "unclassified"
    priority = "low"
    classification_confidence: Optional[float] = None

    # 1. Proximity to Giaspura Industrial Facilities
    if inside_industrial_zone:
        evidence_claims.append(
            f"Spatial proximity: Located within {int(distance_to_facility_m)}m of industrial facility '{nearest_facility['name']}' ({nearest_facility['site_type']}). Note: Spatial correlation does not confirm causation."
        )
        risk_score += 35.0
    elif distance_to_facility_m <= 1500.0:
        evidence_claims.append(
            f"Moderate proximity: Situated {int(distance_to_facility_m)}m from industrial facility '{nearest_facility['name']}'."
        )
        risk_score += 15.0

    # 2. Landcover context
    evidence_claims.append(f"Landcover context: Classified as '{landcover}'.")
    if "Industrial" in landcover:
        risk_score += 15.0

    # 3. Temporal Persistence & Recurrence
    persistence = temporal_summary.get("persistence", "single_observation")
    det_30d = temporal_summary.get("detections_30d", 0)

    if persistence in ["high_persistence", "recurrent_heat_source"]:
        evidence_claims.append(
            f"Temporal pattern: High persistence observed ({det_30d} detections in 30 days). Recurrent thermal signatures in industrial sectors indicate stationary heat emissions (e.g. furnaces, boilers, stack flaring)."
        )
        risk_score += 25.0
    elif persistence == "moderate_persistence":
        evidence_claims.append("Temporal pattern: Multiple thermal detections recorded over past observations.")
        risk_score += 10.0
    else:
        evidence_claims.append("Temporal pattern: Single thermal observation recorded.")

    # 4. Fire Radiative Power (FRP) & Diurnal Signal
    if frp is not None:
        evidence_claims.append(f"Thermal intensity: Fire Radiative Power (FRP) measured at {frp} MW.")
        if frp >= 20.0:
            risk_score += 15.0
        elif frp >= 10.0:
            risk_score += 10.0

    if daynight == "N":
        evidence_claims.append("Diurnal signal: Nocturnal thermal anomaly detected (nighttime industrial thermal emission).")
        risk_score += 10.0

    # Final Classification decision based on cumulative evidence
    risk_score = min(round(risk_score, 1), 100.0)

    if inside_industrial_zone and (persistence in ["high_persistence", "recurrent_heat_source"] or (frp and frp >= 10.0)):
        classification = "industrial_heat_source"
        priority = "high" if risk_score >= 70.0 else "medium"
        classification_confidence = round(min(risk_score / 100.0, 0.95), 2)
    elif inside_industrial_zone or "Industrial" in landcover:
        classification = "industrial_heat_source"
        priority = "medium" if risk_score >= 50.0 else "low"
        classification_confidence = 0.65
    elif "Agricultural" in landcover and persistence == "single_observation":
        classification = "agricultural_burning"
        priority = "medium" if frp and frp > 15.0 else "low"
        classification_confidence = 0.60
    else:
        classification = "unclassified"
        priority = "high" if risk_score >= 75.0 else ("medium" if risk_score >= 45.0 else "low")
        classification_confidence = None

    return {
        "classification": classification,
        "classification_method": "evidence_based",  # Strict flag per requirement
        "classification_confidence": classification_confidence,
        "risk_score": risk_score,
        "priority": priority,
        "evidence": evidence_claims
    }
