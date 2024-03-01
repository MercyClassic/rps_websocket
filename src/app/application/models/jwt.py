from pydantic import BaseModel, EmailStr


class AuthenticateSchema(BaseModel):
    email: EmailStr
    input_password: str
