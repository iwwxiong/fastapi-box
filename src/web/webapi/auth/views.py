import arrow
import logging
from fastapi import Request, Body, Depends

from webapi.core.base import BaseRouter, BaseResponse
from models.antapt import Users
from utils.common_func import compute_md5
from webapi.core.depends import login_required
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
async def login(request: Request, auth: AuthSchema):
    dbsession = request.app.state.dbsession
    user = dbsession.query(Users).filter_by(username=auth.username).first()
    if user is None:
        logger.info(f"Username: {auth.username} is not exists")
        return BaseResponse(status_code=400, message="用户名或密码错误")

    password = compute_md5(auth.password, salt=user.salt)
    if password != user.password:
        return BaseResponse(status_code=400, message="用户名或密码错误")

    user.last_login_time = arrow.now().datetime
    try:
        dbsession.commit()
    except Exception as e:  # noqa
        logger.exception("login failure")
        dbsession.rollback()
        return BaseResponse(status_code=400, message="登录失败")

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
    old_password: str = Body(..., alias="old_password", regex=password_regex, embed=True)
):
    uid = await request.session.get("uid")
    if not uid:
        return BaseResponse(status_code=400, message="用户不存在")

    dbsession = request.app.state.dbsession
    user = dbsession.query(Users).filter_by(id=uid).first()
    if user is None:
        return BaseResponse(status_code=400, message="用户不存在")

    old_hash_password = compute_md5(old_password, salt=user.salt)
    if old_hash_password != user.password:
        return BaseResponse(status_code=400, message="旧密码校验失败")

    salt, hash_password = generate_salt_and_password(password)
    user.salt = salt
    user.password = hash_password
    user.first_login = False
    user.update_time = arrow.now().datetime

    try:
        dbsession.commit()
    except Exception as e:  # noqa
        logger.exception("change_password failure")
        dbsession.rollback()
        return BaseResponse(status_code=400, message="修改密码失败")

    return BaseResponse(message="修改密码成功")
