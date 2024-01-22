import os
from pathlib import Path

from fastapi import FastAPI
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from dependencies.di.init_dependencies import init_dependencies
from routers.game import router as game_router
from routers.users import router as users_router
from routers.jwt import router as jwt_router

root_dir = '%s' % Path(__file__).parent

if not os.path.exists(f'{root_dir}/logs/'):
    os.mkdir(f'{root_dir}/logs/')

logger.add(
    f'{root_dir}/logs/errors.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


def create_app() -> FastAPI:
    app = FastAPI(title='websocket_game')
    init_dependencies(app)
    app.include_router(game_router)
    app.include_router(users_router)
    app.include_router(jwt_router)
    app.mount('/static', StaticFiles(directory='static'), name='static')
    return app


app = create_app()


@app.exception_handler(Exception)
async def unexpected_error_log(request, ex):
    logger.error(ex, exc_info=True)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=None,
    )
