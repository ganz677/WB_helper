import time, sentry_sdk

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from starlette.responses import Response, PlainTextResponse
from prometheus_client import generate_latest

from app.core.settings import settings
from app.observability.loggering import setup_logging
from app.observability.tracing import init_tracing
from app.observability.metrics import http_request_duration, http_requests_total

from app.api import router as api_router

setup_logging(
    level=settings.logging_config.log_level,
    json_logs=True,
    text_format=settings.logging_config.log_format
)
init_tracing()

if settings.sentry.dsn:
    sentry_sdk.init(dsn=settings.sentry.dsn, traces_sample_rate=1.0)


app = FastAPI(
    title='AI_WB_AUTOANSWER',
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],

)

app.include_router(
    api_router
)


@app.middleware("http")
async def metrics_mw(request: Request, call_next):
    start = time.perf_counter()
    status_code = 500
    try:
        response: Response = await call_next(request)
        status_code = response.status_code
        return response
    finally:
        path = request.url.path or "/"
        method = request.method
        dur = time.perf_counter() - start
        http_requests_total.labels(path, method, str(status_code)).inc()
        http_request_duration.labels(path, method).observe(dur)


@app.get(
    path='/healthz'
)
async def healthz():
    return {
        'status': 'ok'
    }

@app.get(
    path='/metrics'
)
async def metrics():
    return PlainTextResponse(
        generate_latest(),
        media_type='text/plain; version=0.0.4'
    )