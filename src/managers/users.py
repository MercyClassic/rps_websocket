import hashlib
import os

from starlette import status
from starlette.exceptions import HTTPException

from interfaces.encoders.jwt import JWTEncoderInterface


class UserManager:
    def __init__(
            self,
            jwt_access_secret_key: str,
            jwt_encoder: JWTEncoderInterface,
    ):
        self.jwt_access_secret_key = jwt_access_secret_key
        self.jwt_encoder = jwt_encoder

    def get_user_info_from_access_token(self, access_token: str) -> dict:
        access_token_data = self.jwt_encoder.decode_jwt(
            encoded_jwt=access_token,
            secret=self.jwt_access_secret_key,
        )
        return {
            'user_id': int(access_token_data.get('sub')),
            'is_superuser': access_token_data.get('is_superuser'),
        }

    @staticmethod
    def make_password(value: str) -> str:
        if len(value) < 4:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Length password must be >= 4',
            )
        salt = os.urandom(32)
        password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            value.encode('utf-8'),
            salt,
            100000,
        )
        """ first 64 characters is password, last 64 is salt """
        hashed_password = '%s%s' % (password_hash.hex(), salt.hex())
        return hashed_password

    @staticmethod
    def check_password(input_password: str, password_from_db: str) -> bool:
        salt_from_db = bytes.fromhex(password_from_db[-64:])
        user_input_password_hash = hashlib.pbkdf2_hmac(
            'sha256',
            input_password.encode('utf-8'),
            salt_from_db,
            100000,
        )
        user_input_full_hashed_password = f'{user_input_password_hash.hex()}{salt_from_db.hex()}'
        return user_input_full_hashed_password == password_from_db
