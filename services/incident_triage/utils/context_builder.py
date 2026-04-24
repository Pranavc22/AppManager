from embedding import search_similar_incidents
from services.incident_triage.utils.query import get_incident_by_id, get_incidents_by_ids


def build_incident_context(incident_id: str, top_k: int = 5):
    # Get current incident details
    incident = get_incident_by_id(incident_id)
    if not incident:
        raise ValueError(f"Incident {incident_id} not found")
    
    # if incident['state'].lower() in ('closed', 'resolved'):
    #     raise ValueError(f"Incident {incident_id} has already been closed/resolved.")
    
    # Embedding search 
    query_text = f"{incident['short_description']} {incident['description']}"
    similar = search_similar_incidents(query_text, top_k=top_k)
    similar_ids = [item["incident_id"] for item in similar]
    
    # Historical incidents based on similarity scores
    similar_details = get_incidents_by_ids(similar_ids)
    score_map = {item["incident_id"]: item["similarity"] for item in similar}
    enriched_similar = []
    for inc in similar_details:
        enriched_similar.append({
            **inc,
            "similarity": score_map.get(inc["number"], 0.0)
        })
    enriched_similar = sorted(
        enriched_similar,
        key=lambda x: x["similarity"],
        reverse=True
    )

    return {
        "incident": incident,
        "similar_incidents": enriched_similar
    }