from threading import Timer

from starlette.websockets import WebSocket

from app.domain.exceptions.game import (
    CantChangeStateNow,
    CantConnectToClosedGame,
    CantConnectToOwnGame,
    GameNotFound,
    UnavailableState,
)
from app.domain.models.game import Game
from app.domain.models.player import Player


class GameService:
    def __init__(self):
        self.active_games: list[Game] = []

    @property
    def games_count(self) -> int:
        return len(self.active_games)

    def create_game(self, init_player: Player) -> int:
        number = self.games_count + 1
        game = Game(init_player=init_player, number=number)
        self.active_games.append(game)
        return game.number

    def get_game_list(self, count: int | None = None) -> list[dict[str, str | int]]:
        active_games = self.active_games if not count else self.active_games[:count]
        games = [
            {
                'game_number': game.number,
                'author_username': game.author_username,
            }
            for game in active_games
        ]
        return games

    def close_game(self, websocket: WebSocket, game_number: int) -> None:
        game = self.get_game_by_number(game_number)
        if not game:
            raise GameNotFound
        elif game.is_init_player(websocket):
            self.active_games.remove(game)
        else:
            game.set_active()

    def get_game_by_number(self, game_number: int) -> Game | None:
        for game in self.active_games:
            if game.number == game_number:
                return game

    def delete_game(self, game: Game) -> None:
        self.active_games.remove(game)

    def join_to_game(
            self,
            connected_player: Player,
            game_number: int,
    ) -> dict[str, int | bool]:
        game = self.get_game_by_number(game_number)
        if not game:
            raise GameNotFound
        elif not game.active:
            raise CantConnectToClosedGame
        elif connected_player.game_owner:
            raise CantConnectToOwnGame
        else:
            game.join_player(connected_player)
            return {'game_number': game.number, 'is_init_player_ready': game.init_player.ready}

    def set_ready(
            self,
            websocket: WebSocket,
            game_number: int,
            state: str,
    ) -> dict | None:
        game = self.get_game_by_number(game_number)
        if state not in game.available_states:
            raise UnavailableState
        elif game.finished or game.set_ready(websocket, state) is False:
            raise CantChangeStateNow
        else:
            another_player = game.get_another_player(websocket)
            if another_player and another_player.ready:
                result = self.get_result_response(game)
                Timer(2, self.delete_game, args=(game, )).start()
                return result
            return {'action': 'ready', 'websocket': getattr(another_player, 'websocket', None)}

    def get_result_response(self, game: Game) -> dict[str, str | Player]:
        result, info = game.get_result()
        if result in ('win', 'lose'):
            return {
                'action': 'finish',
                'winner': info['winner'],
                'loser': info['loser'],
                'is_draw': False,
            }
        else:
            return {
                'action': 'finish',
                'is_draw': True,
                'players': info.values(),
            }
