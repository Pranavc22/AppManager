from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"service": "bug_rca", "message": "Bug RCA service endpoint"}