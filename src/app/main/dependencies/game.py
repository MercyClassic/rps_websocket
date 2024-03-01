from app.application.managers.game import GameConnectionManager


def get_game_connection_manager() -> GameConnectionManager:
    return GameConnectionManager()
