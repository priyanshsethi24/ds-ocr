from fastapi import APIRouter
from controllers.ocr_controller import router as ocr_router

router = APIRouter()
router.include_router(ocr_router, prefix="/pdf", tags=["pdf"])
