from fastapi import APIRouter, Depends

from services.incident_triage.agents.incident_solver.main import _build_incident_context
from services.incident_triage.schemas.base_schema import IncidentStatus, IncidentListResponse, IncidentSummary
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
    return _build_incident_context(incident_id)