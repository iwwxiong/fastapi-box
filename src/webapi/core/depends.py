from fastapi import Request, HTTPException
from starlette.status import HTTP_401_UNAUTHORIZED


async def login_required(request: Request) -> None:
    if request.session:
        username = await request.session.get("username")
        if username:
            return username

        raise HTTPException(HTTP_401_UNAUTHORIZED, detail='长时间未操作，请重新登录')
    raise HTTPException(HTTP_401_UNAUTHORIZED, detail='长时间未操作，请重新登录')
