from fastapi import APIRouter, Depends, HTTPException

from services.user_access.agents.user_access_manager.main import *
from services.user_access.utils.query import *
from services.user_access.schemas.base_schema import AccessRequestFilter, AccessRequestListResponse, AnalyzeResponse

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

# , response_model=AnalyzeResponse
@router.get("/analyze")
def get_analysis(req_id: str):
    context = get_request_base(request_id=req_id)
    roles = get_user_roles(context["user_id"])
    permission = get_required_permission(action=context['requested_action'], resource_type=context['resource_type'])
    candidate_roles = get_roles_for_permission(permission)
    history = get_historical_requests(
        action=context['requested_action'],
        resource_type=context['resource_type'],
        scope_id=context['scope_id'],
        request_id=req_id 
    )
    summary_agent = SummaryAgent()
    summary = summary_agent.generate_summary(context)
    return {
        'context' : context,
        'summary': summary,
        'roles': roles,
        'permission': permission,
        'candidate_roles': candidate_roles,
        'history': history
    }