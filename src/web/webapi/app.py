import aioredis
import logging
from fastapi import FastAPI
from fastapi.routing import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException

from settings import settings
from db.fastapi import FastapiAsyncDatabase
from models.fastapi import Users   # noqa
from webapi.core.middleware.session import RedisSessionMiddleware
from webapi.core.middleware.response_time import ResponseTimeMiddleware
from webapi.core.base import BaseRoute, BaseResponse

logger = logging.getLogger("webapi")


async def init_database(async_db: FastapiAsyncDatabase) -> None:
    from webapi.auth.main import create_user  # noqa

    await async_db.create_tables()
    async_session = async_db.make_session()
    async with async_session() as session:
        ok, user = await session.run_sync(
            create_user,
            username="admin",
            password="admin",
            role="admin"
        )
        if not ok and user is None:
            raise Exception("初始化数据库失败")


def register_async_redis(app: FastAPI) -> None:
    """
    request.app.state.redis
    """

    @app.on_event("startup")
    async def startup_event():
        app.state.async_redis = await aioredis.create_redis_pool(settings.fastapi_redis_uri)

    @app.on_event("shutdown")
    async def shutdown_event():
        app.state.async_redis.close()
        await app.state.async_redis.wait_closed()


def register_async_db(app: FastAPI, init_tables: bool = False) -> None:

    async_db = FastapiAsyncDatabase()

    @app.on_event("startup")
    async def startup_event():
        await init_database(async_db)
        app.state.async_db = async_db

    @app.on_event("shutdown")
    async def shutdown_event():
        await app.state.async_db.close()


def create_app(init_tables: bool = False) -> FastAPI:
    app = FastAPI(
        debug=settings.debug,
        title="FastAPI 开箱即用",
        default_response_class=BaseResponse,
        # 生产模式需要关闭文档
        # openapi_url=None,
        # docs_url=None,
        # redoc_url=None
    )
    app.router.route_class = BaseRoute

    register_async_redis(app)
    register_async_db(app, init_tables=init_tables)

    api_v1_router = APIRouter(prefix="/api/v1")

    # 路由注册
    from .auth.views import router as auth_router  # noqa
    api_v1_router.include_router(auth_router)

    from .home.views import router as home_router  # noqa
    api_v1_router.include_router(home_router)

    app.include_router(api_v1_router)

    """
    中间件执行顺序
    A, B, C
    请求是 C -> B -> A
    响应是 A -> B -> C
    """
    app.add_middleware(ResponseTimeMiddleware)
    app.add_middleware(RedisSessionMiddleware, secret_key=settings.secret_key, expire=60 * 60 * 24)
    
    # cors 跨域
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # 覆写 HttpException，RequestValidationError，标准输出
    @app.exception_handler(StarletteHTTPException)
    async def http_exception_handler(request, exc):
        return BaseResponse(status_code=exc.status_code, message=str(exc.detail))

    @app.exception_handler(RequestValidationError)
    async def validation_exception_handler(request, exc):
        return BaseResponse(
            status_code=400,
            message='参数校验失败',
            content=jsonable_encoder({
                "detail": exc.errors(),
                "body": exc.body
            })
        )

    # 捕捉 500 异常，标准输出
    @app.exception_handler(Exception)
    async def exception_handler(request, exc):
        return BaseResponse(
            status_code=500,
            message='Internal Server Error',
            content=[]
        )

    return app
