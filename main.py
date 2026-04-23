from fastapi import FastAPI

from database import initialize_database
from services.bug_rca.router import router as bug_rca_router
from services.incident_triage.router import router as incident_triage_router
from services.user_access.router import router as user_access_router

app = FastAPI(title="App Manager", description="A system that helps manage applications.", version="1.0.0")

app.include_router(bug_rca_router, prefix="/bug-rca", tags=["Bug Report/Logs Summary + RCA"])
app.include_router(incident_triage_router, prefix="/incident-triage", tags=["Intelligent Incident Triage"])
app.include_router(user_access_router, prefix="/user-access", tags=["User Access Management"])

@app.on_event("startup")
def startup():
    initialize_database()

@app.get("/")
def read_root():
    return {"message": "Welcome to App Manager API"}