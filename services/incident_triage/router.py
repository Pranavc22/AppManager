from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"service": "incident_triage", "message": "Incident Triage service endpoint"}