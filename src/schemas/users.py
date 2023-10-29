from fastapi import HTTPException
from pydantic import BaseModel, EmailStr, field_validator, ConfigDict
from pydantic import Field
from starlette import status


class UserCreateSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    name: str
    email: EmailStr
    password1: str
    password2: str

    @field_validator('password2')
    def validate_password(cls, value, values):
        valid_characters = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!#@$_'
        if (
                value != values.data.get('password1')
                or any(i for i in value if i not in valid_characters)
                or len(value) < 4
        ):
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail='Password is invalid',
            )
        return value


class UserReadBaseSchema(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    name: str
    win_count: int = Field(default=0)
    lose_count: int = Field(default=0)
