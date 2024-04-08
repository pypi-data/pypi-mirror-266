# !/usr/bin/env Python3
# -*- coding: utf-8 -*-
# @Author   : zhangzhanqi
# @FILE     : json.py
# @Time     : 2023/11/30 0:46
from datetime import datetime
from typing import Any, Optional, Callable

from fastapix.common.pydantic import pydantic_encoder

try:
    import orjson


    def dumps(__obj: Any,
              default: Optional[Callable[[Any], Any]] = None,
              option: Optional[int] = None, ):
        return orjson.dumps(
            __obj, default=default,
            option=option
        ).decode(encoding="utf-8")


    def loads(__obj: bytes | bytearray | memoryview | str):
        return orjson.loads(__obj)

except ImportError:
    try:
        from ujson import dumps
        from ujson import loads
    except ImportError:
        from json import dumps
        from json import loads


def pydantic_json_serializer(*args, **kwargs) -> str:
    """
    解决 <BaseModel> is not JSON serializable
    engine: AsyncEngine = create_async_engine(database_url, json_serializer=pydantic_json_serializer)
    engine: Engine = create_engine(database_url, json_serializer=pydantic_json_serializer)
    :param args:
    :param kwargs:
    :return:
    """
    return dumps(*args, default=pydantic_encoder, **kwargs)


def convert_datetime_to_chinese(dt: datetime) -> str:
    return dt.strftime('%Y-%m-%d %H:%M:%S.%f')


def convert_datetime_to_timestamp(dt: datetime) -> float:
    return dt.timestamp()

