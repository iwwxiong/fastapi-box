
from fastapi import Request

from webapi.core.base import BaseRouter, BaseResponse
from models.antapt import Users
from utils.common_func import compute_md5
from utils.log_utils import LoggerHelper
from .schema import AuthSchema

router = BaseRouter(tags=['登录'], prefix='/auth')
logger = LoggerHelper("webapi").get_logger()


@router.get('/login')
def refresh_login(request: Request):
    request.session.reset_sid()
    return BaseResponse(content=[])


@router.post('/login', name='登录')
async def login(request: Request, auth: AuthSchema):
    dbsession = request.app.state.dbsession
    user = dbsession.query(Users).filter_by(username=auth.username).first()
    if user is None:
        return BaseResponse(status_code=401, message='用户名或密码错误')

    password = compute_md5(auth.password, salt=user.salt)
    if password != user.password:
        return BaseResponse(status_code=401, message='用户名或密码错误')

    await request.session.set_dict(user.as_dict())
    return user.as_dict()


@router.post('/logout', name='登出')
async def logout(request: Request):
    await request.session.clear()
    return {}
