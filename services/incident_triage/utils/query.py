from database import engine
from sqlalchemy import text

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