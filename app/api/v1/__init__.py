from fastapi import APIRouter
from app.api.v1.wb_feedback_autoanswers.routes import router as wb_router


router = APIRouter(
    prefix='/v1'
)

router.include_router(wb_router)