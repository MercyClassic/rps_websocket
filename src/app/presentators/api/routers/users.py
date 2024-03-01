from typing import Annotated, Any

from fastapi import APIRouter, Depends
from starlette.responses import JSONResponse

from app.application.models.users import UserCreateSchema, UserReadBaseSchema
from app.domain.interfaces.services.users import UserServiceInterface
from app.main.dependencies.auth import get_current_user_info

router = APIRouter(
    prefix='/users',
    tags=['Accounts'],
)


@router.get(
    '/',
    dependencies=[Depends(get_current_user_info)],
    response_model=list[UserReadBaseSchema],
    status_code=200,
)
async def get_users(
        user_service: Annotated[UserServiceInterface, Depends()],
) -> Any:
    users = await user_service.get_users()
    return users


@router.get(
    '/{user_id}',
    dependencies=[Depends(get_current_user_info)],
    response_model=UserReadBaseSchema,
    status_code=200,
)
async def get_user(
        user_id: int,
        user_service: Annotated[UserServiceInterface, Depends()],
) -> JSONResponse:
    user = await user_service.get_user(user_id)
    return user


@router.post(
    '/register',
    response_model=UserReadBaseSchema,
    status_code=201,
)
async def registration(
        user_data: UserCreateSchema,
        user_service: Annotated[UserServiceInterface, Depends()],
) -> JSONResponse:
    user = await user_service.create_user(user_data=user_data.model_dump())
    return user
