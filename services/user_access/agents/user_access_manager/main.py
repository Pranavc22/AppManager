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