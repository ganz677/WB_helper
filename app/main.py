from fastapi import FastAPI
from app.core.settings import settings
from app.log_conf.loggering import setup_logging
from app.api import router as api_router

setup_logging(
    level=settings.logging_config.log_level,
    json_logs=True,
    text_format=settings.logging_config.log_format
)


app = FastAPI(
    title='AI_WB_AUTOANSWER'
)
app.include_router(
    api_router
)