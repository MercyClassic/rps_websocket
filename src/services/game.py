from threading import Timer
from typing import List, Dict

from starlette.websockets import WebSocket

from exceptions.game import (
    not_found,
    cant_connect_to_own_game,
    cant_connect_to_closed_game,
    cant_change_state_now,
    unavailable_state,
)
from models.game import Game


class GameService:

    def __init__(self):
        self.active_games: List[Game] = []

    @property
    def get_games_count(self) -> int:
        return len(self.active_games)

    async def create_game(self, websocket: WebSocket) -> int:
        game = Game()
        number = self.get_games_count + 1
        await game.create(websocket, number)
        self.active_games.append(game)
        return game.number

    async def get_game_list(self, count: int | None = None) -> List[Dict]:
        games = []
        active_games = self.active_games if not count else self.active_games[:count]
        for game in active_games:
            games.append(
                {
                    'game_number': game.number,
                    'author_username': await game.get_author_username(),
                },
            )
        return games

    async def close_game(self, websocket: WebSocket, game_number: int) -> None:
        game = await self.get_game_by_number(game_number)
        if not game:
            await not_found(websocket)
            return

        if game.is_init_player(websocket):
            self.active_games.remove(game)
        else:
            game.set_active()

    async def get_game_by_number(self, game_number: int) -> Game | None:
        for game in self.active_games:
            if game.number == game_number:
                return game
        return None

    def delete_game(self, game: Game) -> None:
        self.active_games.remove(game)

    async def join_to_game(self, websocket: WebSocket, game_number: int) -> dict | None:
        game = await self.get_game_by_number(game_number)
        if not game:
            await not_found(websocket)
            return
        if await game.is_init_player(websocket):
            await cant_connect_to_own_game(websocket)
            return
        if await game.join_player(websocket) is False:
            await cant_connect_to_closed_game(websocket)
            return
        return {'game_number': game.number, 'is_init_player_ready': game.init_player.ready}

    async def set_ready(
            self,
            websocket: WebSocket,
            game_number: int,
            state: str,
    ) -> dict | None:
        if state not in Game.get_available_states():
            await unavailable_state(websocket)
            return

        game = await self.get_game_by_number(game_number)
        if game.finished or await game.set_ready(websocket, state) is False:
            await cant_change_state_now(websocket)
            return

        another_player_ws = await game.get_another_player_ws(websocket)
        if another_player_ws:
            another_player = await game.get_player(another_player_ws)
            if another_player.ready:
                Timer(2, self.delete_game, args=(game, )).start()
                return await self.get_result_response(game)

        return {'action': 'ready', 'websocket': another_player_ws}

    @staticmethod
    async def get_result_response(game: Game) -> dict:
        result = await game.get_result()
        if isinstance(result, dict):
            return {
                'action': 'finish',
                'players': tuple(result.keys()),
            }
        return {
            'action': 'finish',
            'winner': result,
            'loser': await game.get_another_player_ws(result),
        }
