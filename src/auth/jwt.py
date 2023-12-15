from datetime import datetime, timedelta

import jwt
from fastapi import HTTPException
from starlette import status

from config import get_config

ALGORITHM = get_config().ALGORITHM


def generate_jwt(
        data: dict,
        lifetime_seconds: int,
        secret: str,
) -> str:
    payload = data.copy()
    if lifetime_seconds:
        expires_delta = datetime.utcnow() + timedelta(seconds=lifetime_seconds)
        payload['exp'] = expires_delta
    return jwt.encode(payload, secret, ALGORITHM)


def decode_jwt(
        encoded_jwt: str,
        secret: str,
        soft: bool = False,
) -> dict:
    try:
        decoded_token = jwt.decode(
            encoded_jwt,
            secret,
            algorithms=[ALGORITHM],
            options={'verify_signature': False},
        )
    except (jwt.exceptions.InvalidSignatureError, jwt.exceptions.DecodeError):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Could not validate credentials',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    if decoded_token.get('exp') < datetime.utcnow().timestamp():
        if soft:
            """ FOR LOGOUT """
            return {'sub': decoded_token.get('sub')}
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail='Token expired',
            headers={'WWW-Authenticate': 'Bearer'},
        )
    return decoded_token
