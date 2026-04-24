from database import engine
from sqlalchemy import text

def get_closed_incidents():
    query = text("""
        SELECT 
            Number as number,
            "Short description" as short_description,
            Description as description,
            State as state,
            Resolution as resolution
        FROM incidents
        WHERE LOWER(State) IN ('closed', 'resolved')
    """)

    with engine.connect() as conn:
        result = conn.execute(query)
        rows = result.fetchall()

    return [row._mapping for row in rows]

def get_incidents(status: str):
    query = text("""
        SELECT 
            Number as number,
            "Short description" as short_description,
            "Assigned To" as assigned_to,
            State as state
        FROM incidents
        WHERE LOWER(State) = :status
    """)
    with engine.connect() as conn:
        result = conn.execute(query, {"status": status})
        rows = result.fetchall()
    
    return rows

def get_incident_by_id(incident_id: str):
    if not incident_id:
        return []

    query = text(f"""
        SELECT 
            Number as number,
            "Short description" as short_description,
            Description as description,
            State as state
        FROM incidents
        WHERE Number = :id
    """)

    with engine.connect() as conn:
        result = conn.execute(query, {"id": incident_id})
        row = result.fetchone()

    return row._mapping if row else None

def get_incidents_by_ids(incident_ids: list[str]):
    if not incident_ids:
        return []

    # Create dynamic placeholders
    placeholders = ", ".join([f":id{i}" for i in range(len(incident_ids))])

    query = text(f"""
        SELECT 
            Number as number,
            "Short description" as short_description,
            Description as description,
            Resolution as resolution,
            State as state
        FROM incidents
        WHERE Number IN ({placeholders})
    """)

    # Build params dict
    params = {f"id{i}": incident_ids[i] for i in range(len(incident_ids))}

    with engine.connect() as conn:
        result = conn.execute(query, params)
        rows = result.fetchall()

    return [row._mapping for row in rows]

def update_incident_resolution(incident_id: str, resolution: str):
    query = text("""
        UPDATE incidents
        SET 
            Resolution = :resolution,
            State = 'Resolved'
        WHERE Number = :incident_id
    """)

    with engine.connect() as conn:
        conn.execute(query, {
            "incident_id": incident_id,
            "resolution": resolution
        })
        conn.commit()
