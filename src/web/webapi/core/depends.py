import typing
from pydantic import ValidationError
from fastapi import Request, HTTPException, Depends
from starlette.status import HTTP_401_UNAUTHORIZED, HTTP_403_FORBIDDEN

from .schema import UserSchema


async def login_required(request: Request) -> UserSchema:
    exception = HTTPException(HTTP_401_UNAUTHORIZED, detail='长时间未操作，请重新登录')
    if not request.session:
        raise exception

    try:
        data = await request.session.hgetall()
        user = UserSchema(**data)
        if not user.username:
            raise exception

        return user
    except ValidationError:
        raise exception


def permission_required(roles: typing.List[str]) -> typing.Callable:
    
    async def decorator(request: Request, user: UserSchema = Depends(login_required)) -> UserSchema:
        if user.role in roles:
            return user

        raise HTTPException(HTTP_403_FORBIDDEN, detail='角色权限校验失败')

    return decorator
