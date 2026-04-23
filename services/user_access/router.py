from fastapi import APIRouter

router = APIRouter()

@router.get("/")
def read_root():
    return {"service": "user_access", "message": "User Access service endpoint"}