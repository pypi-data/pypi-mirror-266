from typing import Union, Optional, Dict, Any

from fastapi import HTTPException
from fastapi.encoders import jsonable_encoder
from pydantic import BaseModel

from fastgenerateapi.settings.register_settings import settings
from starlette.background import BackgroundTask
from starlette.responses import JSONResponse

from fastgenerateapi.pydantic_utils.base_model import JSON_ENCODERS
from fastgenerateapi.schemas_factory import response_factory


# class CommonResponse(BaseModel):
#     success: bool = True
#     code: int = 200
#     message: str = "请求成功"
#     data: Union[dict, str, BaseModel] = {}


class ResponseMixin:

    @staticmethod
    def success(msg: str = "请求成功",
                status_code: int = 200,
                code: Optional[int] = None,
                data: Union[BaseModel, dict, str, None] = None,
                background: Optional[BackgroundTask] = None,
                *args,
                **kwargs):
        if data is None:
            json_compatible_data = {}
        else:
            json_compatible_data = jsonable_encoder(data, custom_encoder=JSON_ENCODERS)
        if code is None:
            code = settings.app_settings.CODE_SUCCESS_DEFAULT_VALUE
        resp = response_factory()(success=True, code=code, message=msg, data=json_compatible_data)
        kwargs.update(resp.dict())
        return JSONResponse(kwargs, status_code=status_code, background=background)

    @staticmethod
    def fail(msg: str = "请求失败",
             status_code: int = 200,
             code: Optional[int] = None,
             success: bool = False,
             data: Union[BaseModel, dict, str, None] = None,
             background: Optional[BackgroundTask] = None,
             headers: Optional[Dict[str, Any]] = None,
             *args,
             **kwargs):

        if data is None:
            json_compatible_data = {}
        else:
            json_compatible_data = jsonable_encoder(data, custom_encoder=JSON_ENCODERS)
        if code is None:
            code = settings.app_settings.CODE_FAIL_DEFAULT_VALUE
        resp = response_factory()(success=success, code=code, message=msg, data=json_compatible_data)
        kwargs.update(resp.dict())
        return JSONResponse(
            kwargs,
            status_code=status_code,
            headers=headers or {"Access-Control-Allow-Origin": '*'},
            background=background
        )

    @staticmethod
    def error(msg: str = "系统繁忙，请稍后再试...",
              status_code: int = 400,
              headers: Optional[Dict[str, Any]] = None,
              *args,
              **kwargs):

        raise HTTPException(
            status_code=status_code,
            detail=msg,
            headers=headers or {"Access-Control-Allow-Origin": '*'},
        )

