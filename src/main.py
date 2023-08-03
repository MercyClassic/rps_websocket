from fastapi import FastAPI
from loguru import logger
from starlette import status
from starlette.responses import JSONResponse
from starlette.staticfiles import StaticFiles

from routers.game import router as game_router
from routers.chat import router as chat_router


logger.add(
    'logs/errors.log',
    format='{time} - {level} - {message}',
    level='ERROR',
    rotation='1 month',
    compression='zip',
)


app = FastAPI(title='websocket_game')

app.mount('/static', StaticFiles(directory='static'), name='static')

app.include_router(game_router)
app.include_router(chat_router)


@app.exception_handler(Exception)
async def unexpected_error_log(request, ex):
    logger.error(ex)
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content=None,
    )
