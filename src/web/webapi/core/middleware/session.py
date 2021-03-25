from starlette.middleware.sessions import SessionMiddleware
from starlette.requests import HTTPConnection
from starlette.datastructures import MutableHeaders
from starlette.types import ASGIApp, Message, Receive, Scope, Send

from ..base import SessionStorage


class RedisSessionMiddleware(SessionMiddleware):

    def __init__(self, app: ASGIApp, expire: int = 10 * 60, **kwargs) -> None:
        super(RedisSessionMiddleware, self).__init__(app, **kwargs)
        self.expire = expire

    async def __call__(self, scope: Scope, receive: Receive, send: Send) -> None:
        if scope["type"] not in ("http", "websocket"):  # pragma: no cover
            await self.app(scope, receive, send)
            return

        connection = HTTPConnection(scope)
        redis = connection.app.state.redis

        if self.session_cookie in connection.cookies:
            sid = connection.cookies[self.session_cookie]
            initial_session_was_empty = False
        else:
            initial_session_was_empty = True
            sid = SessionStorage.generate_sid()

        session = SessionStorage(sid, redis, self.expire)
        if await session.exists():
            method = connection.scope["method"].upper()
            if method == "GET":
                # 如果 GET 访问，重置 session 过期
                await session.expire_reset()
            elif method in ["POST", "PUT", "DELETE"]:
                # 重置 sessionid
                await session.reset_sid()
            
        scope["session"] = session

        async def send_wrapper(message: Message) -> None:
            if message["type"] == "http.response.start":
                if scope["session"]:
                    # We have session data to persist.
                    headers = MutableHeaders(scope=message)
                    header_value = "%s=%s; path=/; Max-Age=%d; %s" % (
                        self.session_cookie,
                        scope["session"].sid,
                        self.max_age,
                        self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
                elif not initial_session_was_empty:
                    # The session has been cleared.
                    headers = MutableHeaders(scope=message)
                    header_value = "%s=%s; %s" % (
                        self.session_cookie,
                        "null; path=/; expires=Thu, 01 Jan 1970 00:00:00 GMT;",
                        self.security_flags,
                    )
                    headers.append("Set-Cookie", header_value)
            await send(message)

        await self.app(scope, receive, send_wrapper)
