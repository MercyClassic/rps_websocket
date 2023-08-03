from starlette.websockets import WebSocket

from exceptions.game import cant_connect_to_closed_game


class Player:
    is_ready: bool = False
    state: str = ''

    def __init__(self, ws: WebSocket):
        self._ws = ws

    async def is_this_player(self, websocket: WebSocket) -> bool:
        return self._ws == websocket

    async def get_username(self):
        #  need to override
        return 'username'

    @property
    def ws(self):
        return self._ws


class Game:
    number = None
    __is_active: bool = True

    async def create(self, ws: WebSocket, number: int) -> None:
        self.__init_player = await self.create_player(ws)
        self.number = number

    async def get_author_username(self):
        return await self.__init_player.get_username()

    @staticmethod
    async def create_player(ws: WebSocket) -> Player:
        return Player(ws)

    async def join_player(self, websocket: WebSocket) -> bool | None:
        if not self.__is_active:
            await cant_connect_to_closed_game(websocket)
            return False
        self.__connected_player = await self.create_player(websocket)
        self.__is_active = False

    async def is_init_player(self, websocket: WebSocket) -> bool:
        return await self.__init_player.is_this_player(websocket)

    async def is_connected_player(self, websocket: WebSocket) -> bool:
        try:
            return await self.__connected_player.is_this_player(websocket)
        except AttributeError:
            return False

    @property
    def is_init_player_ready(self):
        return self.__init_player.is_ready

    @property
    def is_connected_player_ready(self):
        return self.__connected_player.is_ready

    @property
    def players_websocket(self):
        return [self.__connected_player.ws, self.__init_player.ws]

    async def broadcast_to_both(self, message: dict):
        for websocket in self.players_websocket:
            await websocket.send_json(message)
