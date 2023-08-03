import asyncio
from typing import List, Dict

from starlette.websockets import WebSocket

from exceptions.game import not_found, cant_connect_to_own_game
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

    async def get_game_list(self) -> List[Dict]:
        games = []
        for game in self.active_games:
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

    async def get_game_by_number(self, game_number: int):
        for game in self.active_games:
            if game.number == game_number:
                return game
        return None

    async def delete_game(self, game_number: int) -> None:
        await asyncio.sleep(10)
        game = await self.get_game_by_number(game_number)
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
            return
        return {'game_number': game.number, 'is_init_player_ready': game.is_init_player_ready}
