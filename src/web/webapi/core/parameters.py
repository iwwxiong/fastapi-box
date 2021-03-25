import arrow
import typing
from datetime import datetime

from fastapi import Query
from starlette.exceptions import HTTPException as StarletteHTTPException


async def datetime_parameters(
    interval_time: int = Query(None, description="时间间隔", gt=0),
    start_time: typing.Optional[datetime] = Query(None, description="开始时间"),
    end_time: typing.Optional[datetime] = Query(None, description="结束时间")
) -> typing.Dict:
    if interval_time:
        end_time = arrow.now()
        start_time = end_time.shift(days=0 - interval_time)

        end_time = end_time.datetime
        start_time = start_time.datetime

    if interval_time is None:
        if start_time is None or end_time is None:
            raise StarletteHTTPException(400, "开始时间和结束时间是必填项")

    if start_time >= end_time:
        raise StarletteHTTPException(400, "开始时间不能小于结束时间")

    return {
        "start_time": start_time,
        "end_time": end_time
    }


async def page_parameters(
    page: int = Query(0, description="页码", ge=0),
    limit: int = Query(20, description="每页大小", ge=10, le=100)
) -> typing.Dict:
    return {"limit": limit, "page": page}


def time_interval(start_time: datetime, end_time: datetime) -> (str, typing.List[arrow.Arrow]):
    start = arrow.get(start_time)
    end = arrow.get(end_time)
    delta = end - start
    _format, result = '%Y-%m-%d %H:%M:%S', []
    if delta.total_seconds() <= 3600 * 24:
        # 1天返回24小时
        result = [h for h in arrow.Arrow.span_range('hour', start, end)]
        # _format = '%Y-%m-%d %H:%M:%S'
    elif delta.days <= 7:
        # 1 周返回7天
        result = [d for d in arrow.Arrow.span_range('day', start, end)]
        # _format = '%Y-%m-%d'
    elif delta.days <= 30:
        # 1月返回30天
        result = [d for d in arrow.Arrow.span_range('day', start, end)]
        # _format = '%Y-%m-%d'
    else:
        # 超过月的话，按月返回
        result = [m for m in arrow.Arrow.span_range('month', start, end)]
        # _format = '%Y-%m'
    if len(result) > 0:
        # 替换首次时间为开始时间
        result[0] = list(result[0])
        result[0][0] = start
        result[0] = tuple(result[0])
        # 替换最后时间为结束时间
        result[-1] = list(result[-1])
        result[-1][1] = end
        result[-1] = list(result[-1])
    return _format, result
