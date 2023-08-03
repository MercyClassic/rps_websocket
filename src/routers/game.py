from fastapi import APIRouter
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from managers.game import manager

router = APIRouter(
    prefix='/game',
    tags=['Game'],
)

templates = Jinja2Templates(directory='templates')


@router.get('')
async def get_games(request: Request):
    return templates.TemplateResponse('game.html', {'request': request})


@router.websocket('/ws')
async def game(websocket: WebSocket):
    await manager.connect(websocket)
