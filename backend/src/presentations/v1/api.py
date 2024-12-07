from fastapi import APIRouter

from src.presentations.v1.data import router as data_router

router = APIRouter(prefix="/v1", tags=["routes v1"])

router.include_router(data_router)
