from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/health")
def version():
    return JSONResponse(content={"status": "up"})
