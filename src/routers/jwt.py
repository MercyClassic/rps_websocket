from fastapi import APIRouter, Depends
from starlette import status
from starlette.requests import Request
from starlette.responses import JSONResponse

from dependencies.users import get_user_service
from schemas.jwt import AuthenticateSchema
from services.jwt import JWTService
from services.users import UserService
from dependencies.jwt import get_jwt_service


router = APIRouter(
    prefix='/auth',
    tags=['JWT'],
)


@router.post('/login')
async def login(
        authenticate_data: AuthenticateSchema,
        jwt_service: JWTService = Depends(get_jwt_service),
        user_service: UserService = Depends(get_user_service),
):
    user_id = await user_service.authenticate(**authenticate_data.model_dump())
    tokens = await jwt_service.create_auth_tokens(user_id)
    response = JSONResponse(status_code=status.HTTP_200_OK, content=tokens.get('access_token'))
    response.set_cookie(key='refresh_token', value=tokens.get('refresh_token'), httponly=True)
    return response


@router.post('/refresh_token')
async def refresh_access_token(
        request: Request,
        jwt_service: JWTService = Depends(get_jwt_service),
):
    tokens = await jwt_service.refresh_auth_tokens(request.cookies.get('refresh_token'))
    response = JSONResponse(status_code=status.HTTP_200_OK, content=tokens.get('access_token'))
    response.set_cookie(key='refresh_token', value=tokens.get('refresh_token'), httponly=True)
    return response


@router.post('/logout')
async def logout(
        request: Request,
        jwt_service: JWTService = Depends(get_jwt_service),
):
    await jwt_service.delete_refresh_token(request.cookies.get('refresh_token'))
    response = JSONResponse(status_code=status.HTTP_401_UNAUTHORIZED, content=None)
    response.delete_cookie('refresh_token')
    return response
