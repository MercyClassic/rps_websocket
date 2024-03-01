from fastapi.websockets import WebSocket, WebSocketDisconnect

from app.application.exceptions.game import (
    cant_change_state_now,
    cant_connect_to_closed_game,
    cant_connect_to_own_game,
    game_not_found,
    unavailable_state,
)
from app.domain.exceptions.game import (
    CantChangeStateNow,
    CantConnectToClosedGame,
    CantConnectToOwnGame,
    GameNotFound,
    UnavailableState,
)
from app.domain.interfaces.services.users import UserServiceInterface
from app.domain.models.player import Player
from app.domain.services.game import GameService


class BaseGameConnectionManager:
    actions: list[str]
    connections: list[WebSocket]
    user_service: UserServiceInterface

    async def handle(self, websocket: WebSocket, data: dict) -> None:
        raise NotImplementedError

    def set_user_service(self, user_service: UserServiceInterface):
        self.user_service = user_service

    async def connect(self, websocket: WebSocket) -> None:
        await websocket.accept()
        self.connections.append(websocket)
        await self.on_connect(websocket)
        try:
            while True:
                data = await websocket.receive_json()
                await self.handle(websocket, data)
        except WebSocketDisconnect:
            await self.disconnect(websocket)

    async def action_not_allowed(self, websocket: WebSocket, _: dict) -> None:
        await websocket.send_json({'action': 'Not found.'})

    async def action_not_found(self, websocket: WebSocket, _: dict) -> None:
        await websocket.send_json({'action': 'Not found.'})

    async def disconnect(self, websocket: WebSocket) -> None:
        self.connections.remove(websocket)
        await self.on_disconnect(websocket)

    async def on_disconnect(self, websocket: WebSocket) -> None:
        pass

    async def on_connect(self, websocket: WebSocket) -> None:
        pass

    async def broadcast(self, message: dict) -> None:
        for connection in self.connections:
            await connection.send_json(message)


class GameConnectionManager(BaseGameConnectionManager):
    def __init__(self) -> None:
        super().__init__()
        self.service = GameService()
        self.connections = []
        self.actions = ['create', 'get_list', 'join', 'ready', 'close']

    async def handle(self, websocket: WebSocket, data: dict) -> None:
        action = data['action']
        if action in self.actions:
            handler = getattr(self, action, self.action_not_found)
        else:
            handler = self.action_not_allowed
        await handler(websocket, data)

    async def on_connect(self, websocket: WebSocket) -> None:
        game_list = self.service.get_game_list(count=10)
        await websocket.send_json({'action': 'first_ten', 'game_list': game_list})

    async def create(self, websocket: WebSocket, *args) -> None:
        token = websocket.headers.get('Authorization')
        if token:
            db_user = await self.user_service.get_user_by_token(token)
        else:
            db_user = None
        init_player = Player(websocket, db_user, is_game_owner=True)
        game_number = self.service.create_game(init_player)
        await websocket.send_json(
            {
                'action': 'create',
                'game_info': {
                    'game_number': game_number,
                    'is_init_player_ready': False,
                },
            },
        )

        game_list = self.service.get_game_list(count=10)
        await self.broadcast({'action': 'first_ten', 'game_list': game_list})

    async def get_list(self, websocket: WebSocket, *args) -> None:
        game_list = self.service.get_game_list()
        await websocket.send_json({'action': 'get_all', 'game_list': game_list})

    async def close(self, websocket: WebSocket, data: dict) -> None:
        game_number = int(data.get('game_number'))
        try:
            self.service.close_game(websocket, game_number)
        except GameNotFound:
            await game_not_found(websocket)
        await websocket.send_json({'action': 'close'})

    async def join(self, websocket: WebSocket, data: dict) -> None:
        game_number = int(data.get('game_number'))

        token = websocket.headers.get('Authorization')
        if token:
            db_user = await self.user_service.get_user_by_token(token)
        else:
            db_user = None
        connected_player = Player(websocket, db_user, is_game_owner=False)

        try:
            game_info = self.service.join_to_game(connected_player, game_number)
        except GameNotFound:
            await game_not_found(connected_player.websocket)
        except CantConnectToClosedGame:
            await cant_connect_to_closed_game(connected_player.websocket)
        except CantConnectToOwnGame:
            await cant_connect_to_own_game(connected_player.websocket)
        else:
            await websocket.send_json({'action': 'join', 'game_info': game_info})

    async def ready(self, websocket: WebSocket, data: dict) -> None:  # noqa: CCR001
        game_number = int(data.get('game_number'))
        state = data.get('state')
        try:
            info = self.service.set_ready(websocket, game_number, state)
        except UnavailableState:
            await unavailable_state(websocket)
        except CantChangeStateNow:
            await cant_change_state_now(websocket)
        else:
            if info:
                action = info.get('action')
                if action == 'ready':
                    websocket_to_broadcast = info.get('websocket')
                    if websocket_to_broadcast:
                        await websocket_to_broadcast.send_json({'action': 'ready'})

                if action == 'finish':
                    await self.process_finish(info)

    async def process_finish(self, info: dict[str, str | Player]) -> None:
        if info['is_draw']:
            for player in info.get('players'):
                await player.websocket.send_json({'action': 'draw'})
        else:
            winner = info.get('winner')
            loser = info.get('loser')
            await winner.websocket.send_json({'action': 'win'})
            await loser.websocket.send_json({'action': 'lose'})
            if winner_id := winner.user_id:
                await self.user_service.update_win(winner_id)
            if loser_id := loser.user_id:
                await self.user_service.update_lose(loser_id)
