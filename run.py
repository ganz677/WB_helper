import uvicorn
from app.core.settings import settings


if __name__ == '__main__':
    uvicorn.run(
        app='app.main:app',
        host=settings.run.host,
        port=settings.run.port,
        reload=settings.run.reload
    )