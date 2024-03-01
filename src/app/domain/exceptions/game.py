from app.domain.exceptions.base import DomainException


class GameNotFound(DomainException):
    pass


class CantConnectToOwnGame(DomainException):
    pass


class CantConnectToClosedGame(DomainException):
    pass


class CantChangeStateNow(DomainException):
    pass


class UnavailableState(DomainException):
    pass
