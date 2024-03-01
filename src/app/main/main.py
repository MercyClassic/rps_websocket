import logging
import sys

from fastapi import FastAPI
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from app.main.dependencies.di.init_dependencies import init_dependencies
from app.presentators.api.routers.game import router as game_router
from app.presentators.api.routers.jwt import router as jwt_router
from app.presentators.api.routers.users import router as users_router

logging.basicConfig(level=logging.WARNING, stream=sys.stdout)
logger = logging.getLogger(__name__)


def create_app() -> FastAPI:
    app = FastAPI(title='websocket_game')
    init_dependencies(app)
    app.include_router(game_router)
    app.include_router(users_router)
    app.include_router(jwt_router)
    app.mount('/static', StaticFiles(directory='app/application/static'), name='static')
    return app


app = create_app()


@app.exception_handler(Exception)
async def unexpected_error_log(request: Request, exc: Exception) -> JSONResponse:
    logger.error(exc, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=None,
    )
