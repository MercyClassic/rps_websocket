from typing import Annotated, List

from fastapi import APIRouter, Depends
from fastapi.encoders import jsonable_encoder
from pydantic import TypeAdapter
from starlette import status
from starlette.responses import JSONResponse

from dependencies.auth import get_current_user_info
from schemas.users import (
    UserCreateSchema,
    UserReadBaseSchema,
)
from services.users import UserServiceInterface


router = APIRouter(
    prefix='/users',
    tags=['Accounts'],
)


@router.get('', dependencies=[Depends(get_current_user_info)])
async def get_users(
        user_service: Annotated[UserServiceInterface, Depends()],
) -> JSONResponse:
    users = await user_service.get_users()
    data = jsonable_encoder(
        TypeAdapter(List[UserReadBaseSchema]).validate_python(users),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.get('/{user_id}', dependencies=[Depends(get_current_user_info)])
async def get_user(
        user_id: int,
        user_service: Annotated[UserServiceInterface, Depends()],
) -> JSONResponse:
    user = await user_service.get_user(user_id)
    data = jsonable_encoder(
        TypeAdapter(UserReadBaseSchema).validate_python(user),
    )
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content=data,
    )


@router.post('/register')
async def registration(
        user_data: UserCreateSchema,
        user_service: Annotated[UserServiceInterface, Depends()],
) -> JSONResponse:
    user = await user_service.create_user(user_data=user_data.model_dump())
    data = jsonable_encoder(
        TypeAdapter(UserReadBaseSchema).validate_python(user),
    )
    return JSONResponse(
        status_code=status.HTTP_201_CREATED,
        content=data,
    )
