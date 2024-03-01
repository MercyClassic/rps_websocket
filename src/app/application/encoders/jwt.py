from datetime import datetime, timedelta

import jwt

from app.application.exceptions.auth import CouldNotValidateCredentials, TokenExpired
from app.application.interfaces.encoders.jwt import JWTEncoderInterface


class JWTEncoder(JWTEncoderInterface):
    def __init__(self, algorithm: str):
        self.algorithm = algorithm

    def generate_jwt(
            self,
            data: dict,
            lifetime_seconds: int,
            secret: str,
    ) -> str:
        payload = data.copy()
        if lifetime_seconds:
            expires_delta = datetime.utcnow() + timedelta(seconds=lifetime_seconds)
            payload['exp'] = expires_delta
        return jwt.encode(payload, secret, self.algorithm)

    def decode_jwt(
            self,
            encoded_jwt: str,
            secret: str,
            soft: bool = False,
    ) -> dict:
        try:
            decoded_token = jwt.decode(
                encoded_jwt,
                secret,
                algorithms=[self.algorithm],
                options={'verify_signature': False},
            )
        except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
            raise CouldNotValidateCredentials
        if decoded_token.get('exp') < datetime.utcnow().timestamp():
            if soft:
                """ FOR LOGOUT """
                return {'sub': decoded_token.get('sub')}
            raise TokenExpired
        return decoded_token
