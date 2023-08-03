from fastapi import APIRouter
from starlette.requests import Request
from starlette.templating import Jinja2Templates
from starlette.websockets import WebSocket

from managers.chat import manager

router = APIRouter(
    prefix='/chat',
    tags=['Chat'],
)

templates = Jinja2Templates(directory='templates')


@router.get('')
async def get_chat(request: Request):
    return templates.TemplateResponse('chat.html', {'request': request})


@router.websocket('/ws/{client_id}')
async def connect_to_chat(websocket: WebSocket, client_id: int):
    await manager.connect(websocket, client_id)
