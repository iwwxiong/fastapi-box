import uuid
import json
import typing

from aioredis import Redis
from fastapi import Request, Response
from fastapi.responses import JSONResponse
from fastapi.routing import APIRoute, APIRouter
from typing import Any, Callable, Coroutine


class SessionStorage:

    session_prefix = 'session:'

    @staticmethod
    def generate_sid() -> str:
        return str(uuid.uuid4())

    async def reset_sid(self):
        """
        删除之前 sid 信息
        """
        old_key = self.session_prefix + self.sid
        self.sid = self.generate_sid()
        self.key = self.session_prefix + self.sid
        data: typing.Dict = await self.redis.hgetall(old_key)
        await self.redis.delete(old_key)
        if data:
            await self.redis.hmset_dict(self.key, data)
            await self.redis.expire(self.key, self.expire)

    def __init__(self, sid: str, redis: Redis, expire: int, **kwargs) -> None:
        self.sid = sid
        self.redis = redis
        self.expire = expire
        self.key = self.session_prefix + self.sid

    async def exists(self) -> bool:
        return bool(await self.redis.exists(self.key))

    async def expire_reset(self) -> None:
        return await self.redis.expire(self.key, self.expire)

    async def get(self, key: typing.Any) -> typing.Any:
        data: typing.Dict = await self.redis.hgetall(self.key)
        return data.get(key)

    async def hgetall(self) -> typing.Dict:
        return await self.redis.hgetall(self.key)

    async def set(self, key: typing.Any, value: typing.Any) -> None:
        pipe = self.redis.pipeline()
        pipe.hmset(self.key, key, value)
        pipe.expire(self.key, self.expire)
        await pipe.execute()

    async def set_dict(self, value: typing.Dict) -> None:
        await self.redis.hmset_dict(self.key, value)
        await self.redis.expire(self.key, self.expire)

    async def pop(self, key: typing.Any) -> None:
        pipe = self.redis.pipeline()
        pipe.hdel(self.key, key)
        pipe.expire(self.key, self.expire)
        await pipe.execute()

    async def clear(self) -> None:
        await self.redis.delete(self.key)

    # def __getitem__(self, key: typing.Any) -> typing.Any:
    #     pass

    # def __delitem__(self, key: typing.Any) -> None:
    #     pass

    # def __setitem__(self, key: typing.Any, value: typing.Any) -> None:
    #     pass


class BaseRequest(Request):

    @property
    def session(self) -> SessionStorage:
        assert (
            "session" in self.scope
        ), "SessionMiddleware must be installed to access request.session"
        return self.scope["session"]


class BaseResponse(JSONResponse):

    def __init__(self, status_code: int = 200, message: str = "OK", content: Any = [], **kwargs) -> None:
        self.message = message
        self.status = status_code
        # 所有的 HTTP status_code 重置为 200，通过响应内容的 status_code 区分异常
        super().__init__(status_code=200, content=content, **kwargs)

    def render(self, content: typing.Any) -> bytes:
        data = {
            "status_code": self.status,
            "message": self.message,
            "data": content
        }
        return json.dumps(
            data,
            ensure_ascii=False,
            allow_nan=False,
            indent=None,
            separators=(",", ":"),
        ).encode("utf-8")


class BaseRoute(APIRoute):

    def get_route_handler(self) -> Callable[[Request], Coroutine[Any, Any, Response]]:
        route_handler = super(BaseRoute, self).get_route_handler()

        async def base_route_handler(request: Request) -> Response:
            request = BaseRequest(request.scope, request.receive)
            return await route_handler(request)

        return base_route_handler


class BaseRouter(APIRouter):

    def __init__(self, **kwargs):
        super().__init__(
            default_response_class=BaseResponse,
            route_class=BaseRoute,
            **kwargs
        )
