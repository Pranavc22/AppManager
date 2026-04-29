from fastapi import APIRouter, Depends

from embedding import add_incident_to_faiss
from services.incident_triage.agents.incident_solver.main import IncidentAnalysisAgent
from services.incident_triage.schemas.base_schema import IncidentStatus, IncidentListResponse, IncidentSummary, SimilarIncident, IncidentAnalysisResponse, IncidentResolveRequest, IncidentCreateRequest
from services.incident_triage.utils.context_builder import build_incident_context
from services.incident_triage.utils.query import get_incidents, update_incident_resolution, get_incident_by_id, create_incident, get_latest_incident_number

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

@router.post("/resolve")
def resolve_incident(request: IncidentResolveRequest):

    # Update DB
    update_incident_resolution(
        request.incident_id,
        request.resolution
    )

    # Fetch updated record
    incident = get_incident_by_id(request.incident_id)

    if not incident:
        raise ValueError("Incident not found")

    # Add to FAISS
    add_incident_to_faiss(incident)

    return {
        "message": "Incident resolved and indexed successfully",
        "incident_id": request.incident_id
    }

@router.post("/create-incident")
def create_new_incident(request: IncidentCreateRequest):
    latest_number = get_latest_incident_number()
    prefix = latest_number[:3]
    num_str = latest_number[3:]
    new_number = f"{prefix}{int(num_str) + 1}"

    incident_data = {
        "affected_user": request.affected_user,
        "number": new_number,
        "short_description": request.short_description,
        "description": request.description,
        "assigned_to": request.assigned_to,
        "state": "Open",
        "resolution": request.resolution
    }
    
    create_incident(incident_data)

    return {
        "message": "Incident created successfully",
        "incident_id": new_number
    }
