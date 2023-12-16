import os
from typing import Dict

from starlette.websockets import WebSocket

from db.database import async_session_maker
from encoders.jwt import JWTEncoder
from managers.users import UserManager
from db.models.users import User
from repositories.users import UserRepository


class Player:
    __ready: bool = False
    __state: str = ''
    __db_user: User | None = None

    def __init__(self, ws: WebSocket):
        self.__ws = ws
        self.repository = UserRepository(async_session_maker())  # cringe

    async def create_db_user(self, token):
        user_id = (
            UserManager(
                os.environ['JWT_ACCESS_SECRET_KEY'],
                JWTEncoder(os.environ['ALGORITHM']),
            )
            .get_user_info_from_access_token(token)
            .get('user_id')
        )
        self.__db_user = await self.repository.get_one(user_id)

    async def is_this_player(self, websocket: WebSocket) -> bool:
        return self.__ws == websocket

    async def get_username(self) -> str:
        if self.__db_user:
            return self.__db_user.name
        return 'AnonymousUser'

    async def set_win(self) -> None:
        if self.__db_user:
            await self.repository.update_win(self.__db_user.id)

    async def set_lose(self) -> None:
        if self.__db_user:
            await self.repository.update_lose(self.__db_user.id)

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
    __init_player: Player = None
    __connected_player: Player = None

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
        player = Player(ws)
        token = ws.headers.get('Authorization')
        if token:
            await player.create_db_user(token)
        return player

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
            await self.finish_game(winner=self.__init_player, loser=self.__connected_player)
            return self.__init_player.ws
        elif result == 'L':
            await self.finish_game(winner=self.__connected_player, loser=self.__init_player)
            return self.__connected_player.ws
        elif result == 'D':
            return self.players_websocket

    async def finish_game(self, winner: Player, loser: Player):
        self.__finished = True
        await winner.set_win()
        await loser.set_lose()

    @property
    def players_websocket(self) -> Dict[WebSocket, str]:
        websockets = {self.__init_player.ws: 'init_player'}
        try:
            websockets.update({self.__connected_player.ws: 'connected_player'})
        except AttributeError:
            pass
        finally:
            return websockets

    async def get_another_player_ws(self, websocket: WebSocket) -> WebSocket | None:
        websockets = self.players_websocket
        websockets.pop(websocket, None)
        try:
            return tuple(websockets.keys())[0]
        except IndexError:
            return
