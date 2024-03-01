from typing import Annotated

from fastapi import APIRouter, Depends
from starlette.requests import Request
from starlette.responses import Response
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from app.application.managers.game import BaseGameConnectionManager
from app.domain.interfaces.services.users import UserServiceInterface

router = APIRouter(
    prefix='/game',
    tags=['Game'],
)

templates = Jinja2Templates(directory='app/application/templates')


@router.get('/')
async def get_games(request: Request) -> Response:
    return templates.TemplateResponse('game.html', {'request': request})


@router.websocket('/ws')
async def game(
        websocket: WebSocket,
        manager: Annotated[BaseGameConnectionManager, Depends()],
        user_service: Annotated[UserServiceInterface, Depends()],
) -> None:
    manager.set_user_service(user_service)
    await manager.connect(websocket)
