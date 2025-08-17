from fastapi import APIRouter

router = APIRouter()

@router.get("/assignments/health")
async def health_check():
    return {"status": "ok"}