from fastapi import FastAPI
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from db.database import get_async_session, get_session_stub
from dependencies.jwt import get_jwt_service
from dependencies.users import get_user_service
from routers.game import router as game_router
from routers.users import router as users_router
from routers.jwt import router as jwt_router
from services.jwt import JWTServiceInterface
from services.users import UserServiceInterface

logger.add(
    'logs/errors.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


app = FastAPI(title='websocket_game')

app.dependency_overrides[get_session_stub] = get_async_session
app.dependency_overrides[JWTServiceInterface] = get_jwt_service
app.dependency_overrides[UserServiceInterface] = get_user_service

app.mount('/static', StaticFiles(directory='static'), name='static')


@app.exception_handler(Exception)
async def unexpected_error_log(request, ex):
    logger.error(ex)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=None,
    )

app.include_router(game_router)
app.include_router(users_router)
app.include_router(jwt_router)
