from fastapi import APIRouter

from src.presentations.v1 import v1_router

router = APIRouter()

router.include_router(v1_router)


@router.get("/health")
async def health():
    return {"status": "ok"}
