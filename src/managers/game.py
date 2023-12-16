from typing import List

from starlette.websockets import WebSocket, WebSocketDisconnect

from services.game import GameService


class GameConnectionManager:
    actions: List[str] = []

    def __init__(self):
        self.connections: List[WebSocket] = []

    async def handle(self, websocket: WebSocket, data: dict):
        raise NotImplementedError

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


class GameActions(GameConnectionManager):
    service = GameService()
    actions: List[str] = ['create', 'get_list', 'join', 'ready', 'close']

    async def handle(self, websocket: WebSocket, data: dict):
        if data['action'] in self.actions:
            handler = getattr(self, data['action'], self.action_not_allowed)
        else:
            handler = self.action_not_allowed
        result = await handler(websocket, data)
        return result

    async def on_connect(self, websocket: WebSocket) -> None:
        game_list = await self.get_first_ten()
        await websocket.send_json({'action': 'first_ten', 'game_list': game_list})

    async def get_first_ten(self):
        return await self.service.get_game_list(count=10)

    @staticmethod
    async def action_not_allowed(websocket: WebSocket, *args) -> None:
        await websocket.send_json({'action': 'Not found.'})

    async def create(self, websocket: WebSocket, *args) -> None:
        game_number = await self.service.create_game(websocket)
        await websocket.send_json(
            {
                'action': 'create',
                'game_info': {
                    'game_number': game_number,
                    'is_init_player_ready': False,
                },
            },
        )

        game_list = await self.get_first_ten()
        await self.broadcast({'action': 'first_ten', 'game_list': game_list})

    async def get_list(self, websocket: WebSocket, *args) -> None:
        game_list = await self.service.get_game_list()
        await websocket.send_json({'action': 'get_all', 'game_list': game_list})

    async def close(self, websocket: WebSocket, data: dict) -> None:
        game_number = int(data.get('game_number'))
        await self.service.close_game(websocket, game_number)
        await websocket.send_json({'action': 'close'})

    async def join(self, websocket: WebSocket, data: dict) -> None:
        game_number = int(data.get('game_number'))
        game_info = await self.service.join_to_game(websocket, game_number)
        if game_info:
            await websocket.send_json({'action': 'join', 'game_info': game_info})

    async def ready(self, websocket: WebSocket, data: dict) -> None:
        game_number = int(data.get('game_number'))
        state = data.get('state')
        info = await self.service.set_ready(websocket, game_number, state)

        if not info:
            return

        action = info.get('action')
        if action == 'ready':
            websocket_to_broadcast = info.get('websocket')
            if websocket_to_broadcast:
                await websocket_to_broadcast.send_json({'action': 'ready'})
        elif action == 'finish':

            if isinstance(info.get('players'), tuple):
                for player_ws in info.get('players'):
                    await player_ws.send_json({'action': 'draw'})
                return

            winner_websocket = info.get('winner')
            loser_websocket = info.get('loser')
            await winner_websocket.send_json({'action': 'win'})
            await loser_websocket.send_json({'action': 'lose'})


manager = GameActions()
