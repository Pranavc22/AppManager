from fastapi import APIRouter, Depends, HTTPException

from services.user_access.agents.user_access_manager.main import get_access_requests_by_status
from services.user_access.schemas.base_schema import AccessRequestFilter

router = APIRouter()

@router.get("/get-access-requests")
def get_access_requests(filters: AccessRequestFilter = Depends()):
    try:
        data = get_access_requests_by_status(filters.status)

        return {
            "status": "SUCCESS",
            "count": len(data),
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.get("/")
def read_root():
    return {"service": "user_access", "message": "User Access service endpoint"}