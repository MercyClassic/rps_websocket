from starlette.websockets import WebSocket

from app.infrastructure.db.models import User


class Player:
    def __init__(
            self,
            ws: WebSocket,
            user_info: User | None,
            is_game_owner: bool,
    ):
        self.__game_owner = is_game_owner
        self.__ws = ws
        self.__ready = False
        self.__state = ''
        self.__user_info = user_info

    async def is_this_player(self, websocket: WebSocket) -> bool:
        return self.__ws == websocket

    @property
    def username(self) -> str:
        if self.__user_info:
            return self.__user_info.name
        return 'Anonymous User'

    @property
    def user_id(self) -> int | None:
        if self.__user_info:
            return self.__user_info.id

    @property
    def ready(self) -> bool:
        return self.__ready

    def set_ready(self) -> None:
        self.__ready = True

    @property
    def state(self) -> str:
        return self.__state

    @state.setter
    def state(self, state: str) -> None:
        self.__state = state

    @property
    def websocket(self) -> WebSocket:
        return self.__ws

    @property
    def game_owner(self) -> bool:
        return self.__game_owner
