import logging
from typing import Dict, Any, Optional, Tuple
import httpx
from app.core.config import settings

logger = logging.getLogger("llm_service")

async def generate_explanation(analysis_data: Dict[str, Any]) -> Tuple[Optional[str], bool]:
    """
    Pass verified backend facts to local Ollama/Qwen model for natural language summary.
    Strictly instructs the LLM not to invent coordinates, thermal values, or facilities.
    Returns (explanation_text, is_llm_available).
    """
    ollama_url = settings.OLLAMA_BASE_URL.rstrip("/")
    api_endpoint = f"{ollama_url}/api/generate"

    # Format factual payload strictly
    event_id = analysis_data.get("event_id", "Location Investigation")
    lat = analysis_data.get("latitude")
    lon = analysis_data.get("longitude")
    classification = analysis_data.get("classification", "unclassified")
    method = analysis_data.get("classification_method", "evidence_based")
    risk_score = analysis_data.get("risk_score", 0.0)
    priority = analysis_data.get("priority", "low")
    facility = analysis_data.get("nearest_facility_name", "None nearby")
    facility_dist = analysis_data.get("distance_to_facility_m")
    landcover = analysis_data.get("landcover", "Unknown")
    evidence_list = analysis_data.get("evidence", [])

    prompt = f"""You are an objective AI satellite intelligence assistant for FieryVision AI monitoring Giaspura, Ludhiana, Punjab.
Explain the following VERIFIED empirical backend facts to the user in 2 concise sentences. Do not invent any new coordinates, thermal readings, or facilities.

VERIFIED BACKEND FACTS:
- Target ID: {event_id}
- Location: Lat {lat}, Lon {lon}
- Classification: {classification} (Method: {method})
- Risk Score: {risk_score}/100 | Priority: {priority}
- Nearest Industrial Facility: {facility} (Distance: {facility_dist} meters)
- Landcover Context: {landcover}
- Key Evidence: {"; ".join(evidence_list)}

Write a factual summary based strictly on the above evidence.
"""

    payload = {
        "model": "qwen:7b",  # or qwen2.5 / qwen:latest
        "prompt": prompt,
        "stream": False
    }

    try:
        async with httpx.AsyncClient(timeout=4.0) as client:
            response = await client.post(api_endpoint, json=payload)
            if response.status_code == 200:
                result = response.json()
                text = result.get("response", "").strip()
                if text:
                    return text, True
    except Exception as e:
        logger.info(f"Ollama/Qwen service unreachable at {ollama_url}: {str(e)}")

    # Deterministic factual fallback explanation when LLM is unavailable
    fallback_text = (
        f"Event '{event_id}' at ({lat}, {lon}) is categorized as '{classification}' "
        f"with a risk score of {risk_score}/100 ({priority} priority) based on {method} assessment. "
        f"Nearest facility: {facility} ({int(facility_dist) if facility_dist is not None else 'N/A'}m). "
        "[Note: Qwen LLM explanation service offline; returning structured empirical evidence directly]."
    )
    return fallback_text, False
