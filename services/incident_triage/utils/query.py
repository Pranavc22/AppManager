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


def _generate_next_incident_number(conn):
    query = text("""
        SELECT COALESCE(MAX(CAST(SUBSTR(Number, 4) AS INTEGER)), 4001000) AS max_num
        FROM incidents
        WHERE Number LIKE 'INC%'
    """)
    row = conn.execute(query).fetchone()
    return f"INC{int(row[0]) + 1}"


def create_incident(number: str, short_description: str, assigned_to: str, state: str):
    insert_query = text("""
        INSERT INTO incidents (
            "Affected User",
            Number,
            "Short description",
            Description,
            "Assigned To",
            State,
            Resolution
        )
        VALUES (
            :affected_user,
            :number,
            :short_description,
            :description,
            :assigned_to,
            :state,
            :resolution
        )
    """)

    with engine.connect() as conn:
        conn.execute(insert_query, {
            "affected_user": "",
            "number": number,
            "short_description": short_description,
            "description": "",
            "assigned_to": assigned_to,
            "state": state,
            "resolution": "",
        })
        conn.commit()

    return number
