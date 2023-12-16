from abc import ABC, abstractmethod


class JWTEncoderInterface(ABC):
    @abstractmethod
    def generate_jwt(
            self,
            data: dict,
            lifetime_seconds: int,
            secret: str,
    ) -> str:
        raise NotImplementedError

    @abstractmethod
    def decode_jwt(
            self,
            encoded_jwt: str,
            secret: str,
            soft: bool = False,
    ) -> dict:
        raise NotImplementedError
