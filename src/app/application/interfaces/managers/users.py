class UserManagerInterface:
    def get_user_info_from_access_token(self, access_token: str) -> dict[str, str | bool]:
        raise NotImplementedError

    @staticmethod
    def make_password(value: str) -> str:
        raise NotImplementedError

    @staticmethod
    def check_password(input_password: str, password_from_db: str) -> bool:
        raise NotImplementedError
