import logging
import datetime
from fastapi import Request, Body, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import update

from webapi.core.base import BaseRouter, BaseResponse
from models.fastapi import Users
from utils.common_func import compute_md5
from webapi.core.depends import login_required, get_async_dbsession
from webapi.core.schema import UserSchema
from fastapi.encoders import jsonable_encoder
from .schema import AuthSchema, password_regex
from .main import generate_salt_and_password

router = BaseRouter(tags=["登录"], prefix="/auth")
logger = logging.getLogger("webapi")


@router.get("/login")
async def refresh_login(request: Request):
    await request.session.clear()
    return BaseResponse(content=[])


@router.post("/login", name="登录", response_model=UserSchema)
async def login(request: Request, auth: AuthSchema, dbsession: AsyncSession = Depends(get_async_dbsession)):
    stmt = select(Users).where(Users.username == auth.username)
    result = await dbsession.execute(stmt)
    user = result.scalars().first()
    if user is None:
        logger.info(f"Username: {auth.username} is not exists")
        return BaseResponse(status_code=400, message="用户名或密码错误")

    password = compute_md5(auth.password, salt=user.salt)
    if password != user.password:
        return BaseResponse(status_code=400, message="用户名或密码错误")

    await request.session.set_dict(user.as_dict())
    return BaseResponse(message="登录成功", content=jsonable_encoder(UserSchema(**user.as_dict())))


@router.post("/logout", name="登出")
async def logout(request: Request):
    await request.session.clear()
    return BaseResponse(message="登出成功")


@router.post("/change_password", name="修改密码", dependencies=[Depends(login_required)])
async def change_password(
    request: Request,
    password: str = Body(..., alias="password", regex=password_regex, embed=True),
    old_password: str = Body(..., alias="old_password", regex=password_regex, embed=True),
    dbsession: AsyncSession = Depends(get_async_dbsession)
):
    uid = await request.session.get("uid")
    if not uid:
        return BaseResponse(status_code=400, message="用户不存在")

    uid = int(uid)
    stmt = select(Users).where(Users.id == uid)
    result = await dbsession.execute(stmt)
    user = result.scalars().first()
    if user is None:
        return BaseResponse(status_code=400, message="用户不存在")

    old_hash_password = compute_md5(old_password, salt=user.salt)
    if old_hash_password != user.password:
        return BaseResponse(status_code=400, message="旧密码校验失败")

    salt, hash_password = generate_salt_and_password(password)
    stmt = (update(Users).where(Users.id == uid).values(
        salt=salt,
        password=hash_password,
        update_time=datetime.datetime.now()
    ))
    await dbsession.execute(stmt)

    try:
        await dbsession.commit()
    except Exception as e:  # noqa
        logger.exception("change_password failure")
        await dbsession.rollback()
        return BaseResponse(status_code=400, message="修改密码失败")

    return BaseResponse(message="修改密码成功")
