from typing import Dict

from starlette.websockets import WebSocket


class Player:
    __ready: bool = False
    __state: str = ''

    def __init__(self, ws: WebSocket):
        self.__ws = ws

    async def is_this_player(self, websocket: WebSocket) -> bool:
        return self.__ws == websocket

    async def get_username(self) -> str:
        #  need to override
        return 'username'

    def set_ready(self) -> None:
        self.__ready = True

    @property
    def ready(self) -> bool:
        return self.__ready

    def set_state(self, state: str) -> None:
        self.__state = state

    @property
    def state(self) -> str:
        return self.__state

    @property
    def ws(self) -> WebSocket:
        return self.__ws


class Game:
    number = None
    __active: bool = True
    __finished: bool = False

    @staticmethod
    def get_available_states():
        return 'rock', 'scissors', 'paper'

    @property
    def finished(self) -> bool:
        return self.__finished

    @property
    def active(self) -> bool:
        return self.__active

    def set_active(self):
        self.__active = True

    async def create(self, ws: WebSocket, number: int) -> None:
        self.__init_player = await self.create_player(ws)
        self.number = number

    async def get_author_username(self) -> str:
        return await self.__init_player.get_username()

    @staticmethod
    async def create_player(ws: WebSocket) -> Player:
        return Player(ws)

    async def join_player(self, websocket: WebSocket) -> bool | None:
        if not self.active:
            return False
        self.__connected_player = await self.create_player(websocket)
        self.__active = False

    async def is_init_player(self, websocket: WebSocket) -> bool:
        return await self.__init_player.is_this_player(websocket)

    @property
    def init_player(self) -> Player:
        return self.__init_player

    async def is_connected_player(self, websocket: WebSocket) -> bool:
        try:
            return await self.__connected_player.is_this_player(websocket)
        except AttributeError:
            return False

    @property
    def connected_player(self) -> Player:
        return self.__connected_player

    async def get_player(self, websocket: WebSocket) -> Player | None:
        if await self.is_init_player(websocket):
            return self.__init_player
        elif await self.is_connected_player(websocket):
            return self.__connected_player

    async def set_ready(self, websocket: WebSocket, state: str) -> bool | None:
        player = await self.get_player(websocket)
        if not player:
            return False
        player.set_ready()
        player.set_state(state)

    async def get_result(self) -> WebSocket | Dict[WebSocket, str]:
        state_init_player = self.__init_player.state
        state_connected_player = self.__connected_player.state

        rules = {
            'rock': {'rock': 'D', 'scissors': 'W', 'paper': 'L'},
            'scissors': {'rock': 'L', 'scissors': 'D', 'paper': 'W'},
            'paper': {'rock': 'W', 'scissors': 'L', 'paper': 'D'},
        }

        result = rules[state_init_player][state_connected_player]
        if result == 'W':
            return self.__init_player.ws
        elif result == 'L':
            return self.__connected_player.ws
        elif result == 'D':
            return self.players_websocket

        await self.finish_game()

    async def finish_game(self):
        self.__finished = True

    @property
    def players_websocket(self) -> Dict[WebSocket, str]:
        websockets = {self.__init_player.ws: 'init_player'}
        try:
            websockets.update({self.__connected_player.ws: 'connected_player'})
        except AttributeError:
            return websockets

    async def get_another_player_ws(self, websocket: WebSocket) -> WebSocket | None:
        websockets = self.players_websocket
        websockets.pop(websocket, None)
        try:
            return tuple(websockets.keys())[0]
        except IndexError:
            return
