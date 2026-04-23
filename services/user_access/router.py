from fastapi import APIRouter, Depends, HTTPException

from services.user_access.agents.user_access_manager.main import get_access_requests_by_status
from services.user_access.schemas.base_schema import AccessRequestFilter, AccessRequestListResponse

router = APIRouter()

@router.get("/get-access-requests", response_model=AccessRequestListResponse)
def get_access_requests(filters: AccessRequestFilter = Depends()):
    try:
        data = get_access_requests_by_status(filters.status)

        return {
            "count": len(data),
            "data": data
        }

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

