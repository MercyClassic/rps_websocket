from typing import Literal

from starlette.websockets import WebSocket

from app.domain.models.player import Player


class Game:
    def __init__(self, init_player: Player, number: int) -> None:
        self.number = number
        self.__active = True
        self.__finished = False
        self.__init_player = init_player
        self.__connected_player: Player | None = None

    @property
    def available_states(self):
        return 'rock', 'scissors', 'paper'

    @property
    def finished(self) -> bool:
        return self.__finished

    @property
    def active(self) -> bool:
        return self.__active

    def set_active(self):
        self.__active = True

    @property
    def author_username(self) -> str:
        return self.__init_player.username

    def join_player(self, connected_player: Player) -> None:
        self.__connected_player = connected_player
        self.__active = False

    def is_init_player(self, websocket: WebSocket) -> bool:
        player = self.get_player(websocket)
        return player.game_owner

    def is_connected_player(self, websocket: WebSocket) -> bool:
        if self.__connected_player:
            player = self.get_player(websocket)
            is_connected = not player.game_owner
            return is_connected
        return False

    @property
    def init_player(self) -> Player:
        return self.__init_player

    @property
    def connected_player(self) -> Player:
        return self.__connected_player

    def get_player(self, websocket: WebSocket) -> Player | None:
        for player in self.players:
            if player.websocket == websocket:
                return player

    def set_ready(self, websocket: WebSocket, state: str) -> bool:
        player = self.get_player(websocket)
        if player:
            player.set_ready()
            player.state = state
            return True
        return False

    def get_result(self) -> tuple[Literal['win', 'lose', 'draw'], dict[str, Player]]:
        state_init_player = self.__init_player.state
        state_connected_player = self.__connected_player.state

        rules = {
            'rock': {'rock': 'D', 'scissors': 'W', 'paper': 'L'},
            'scissors': {'rock': 'L', 'scissors': 'D', 'paper': 'W'},
            'paper': {'rock': 'W', 'scissors': 'L', 'paper': 'D'},
        }

        result = rules[state_init_player][state_connected_player]
        if result == 'W':
            self.__finished = True
            return 'win', {
                'winner': self.__init_player,
                'loser': self.__connected_player,
            }
        elif result == 'L':
            self.__finished = True
            return 'lose', {
                'winner': self.__connected_player,
                'loser': self.__init_player,
            }
        elif result == 'D':
            return 'draw', {
                'player_1': self.__connected_player,
                'player_2': self.__init_player,
            }

    @property
    def players(self) -> list[Player]:
        players = [self.__init_player]
        if self.__connected_player:
            players.append(self.__connected_player)
        return players

    def get_another_player(self, websocket: WebSocket) -> Player | None:
        players = self.players
        player = [player for player in players if player.websocket != websocket]
        if player:
            return player[0]
