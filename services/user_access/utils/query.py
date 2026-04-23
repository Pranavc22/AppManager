from sqlalchemy import text

from database import engine

def get_access_requests_by_status(status: str):
    query = text("""
        SELECT 
            ar.request_id,
            ar.user_id,
            u.name AS user_name,
            ar.resource_id,
            r.resource_name,
            ar.requested_action,
            ar.status,
            ar.created_at
        FROM access_requests ar
        JOIN users u ON ar.user_id = u.user_id
        JOIN resources r ON ar.resource_id = r.resource_id
        WHERE LOWER(ar.status) = LOWER(:status)
        ORDER BY ar.created_at DESC
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"status": status})
        rows = result.fetchall()

    return [dict(row._mapping) for row in rows]

def get_request_base(request_id: str):
    query = text("""
        SELECT 
            ar.request_id,
            ar.user_id,
            u.name AS user_name,
            ar.resource_id,
            r.resource_name,
            r.resource_type,
            r.sensitivity,
            ar.requested_action,
            ar.scope_id,
            ar.justification
        FROM access_requests ar
        JOIN users u ON ar.user_id = u.user_id
        JOIN resources r ON ar.resource_id = r.resource_id
        WHERE ar.request_id = :request_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"request_id": request_id}).fetchone()

    return dict(result._mapping) if result else None

def get_user_roles(user_id: str):
    query = text("""
        SELECT 
            r.role_name,
            ur.scope_id
        FROM user_roles ur
        JOIN roles r ON ur.role_id = r.role_id
        WHERE ur.user_id = :user_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"user_id": user_id}).fetchall()

    return [
        {"role": row.role_name, "scope": row.scope_id}
        for row in result
    ]

def get_required_permission(action: str, resource_type: str):
    query = text("""
        SELECT permission_id
        FROM permissions
        WHERE action = :action
          AND resource_type = :resource_type
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "action": action,
            "resource_type": resource_type
        }).fetchone()

    return result.permission_id if result else None

def get_roles_for_permission(permission_id: str):
    query = text("""
        SELECT r.role_name
        FROM role_permissions rp
        JOIN roles r ON rp.role_id = r.role_id
        WHERE rp.permission_id = :permission_id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "permission_id": permission_id
        }).fetchall()

    return [row.role_name for row in result]

def get_historical_requests(action: str, resource_type: str, scope_id: str, request_id: str):
    query = text("""
        SELECT 
            ar.request_id,
            ad.decision,
            ad.decided_at
        FROM access_requests ar
        JOIN resources r ON ar.resource_id = r.resource_id
        JOIN access_decisions ad ON ar.request_id = ad.request_id
        WHERE 
            ar.requested_action = :action
            AND r.resource_type = :resource_type
            AND ar.scope_id = :scope_id
            AND ar.request_id != :request_id
        ORDER BY ad.decided_at DESC
        LIMIT 10
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {
            "action": action,
            "resource_type": resource_type,
            "scope_id": scope_id,
            "request_id": request_id
        }).fetchall()

    approved = []
    rejected = []

    for row in result:

        if row.decision == "APPROVED":
            approved.append(row.request_id)
        elif row.decision == "REJECTED":
            rejected.append(row.request_id)

    return {
        "approved_request_ids": approved,
        "rejected_request_ids": rejected
    }
