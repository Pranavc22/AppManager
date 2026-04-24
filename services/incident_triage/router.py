from fastapi import APIRouter, Depends

from services.incident_triage.agents.incident_solver.main import IncidentAnalysisAgent
from services.incident_triage.schemas.base_schema import IncidentStatus, IncidentListResponse, IncidentSummary, SimilarIncident, IncidentAnalysisResponse
from services.incident_triage.utils.context_builder import build_incident_context
from services.incident_triage.utils.query import get_incidents

router = APIRouter()

@router.get("/")
def read_root():
    return {"service": "incident_triage", "message": "Incident Triage service endpoint"}

@router.get("/get-incidents", response_model=IncidentListResponse)
def get_incidents_by_status(status: str):
    # Validate using schema explicitly
    validated = IncidentStatus(status=status)

    rows = get_incidents(validated.status)

    incidents = [IncidentSummary(**dict(row._mapping)) for row in rows]

    return IncidentListResponse(
        count=len(incidents),
        incidents=incidents
    )

@router.post("/analyze")
def get_analysis(incident_id: str):
    agent = IncidentAnalysisAgent()
    context = build_incident_context(incident_id=incident_id, top_k=3)
    analysis = agent.analyze(context)
    
    # Form response
    similar_incidents = [
        SimilarIncident(
            incident_id=inc["number"],
            short_description=inc["short_description"],
            description=inc.get("description", ""),
            resolution=inc.get("resolution", "")
        )
        for inc in context["similar_incidents"]
    ]

    return IncidentAnalysisResponse(
        **analysis,
        similar_incidents=similar_incidents
    )