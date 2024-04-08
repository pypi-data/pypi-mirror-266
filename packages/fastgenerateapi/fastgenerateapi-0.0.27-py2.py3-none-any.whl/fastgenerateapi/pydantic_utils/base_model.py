from typing import List

from pydantic import BaseModel as PydanticBaseModel, Extra, BaseConfig

from fastgenerateapi.pydantic_utils.json_encoders import JSON_ENCODERS


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders = JSON_ENCODERS
        extra = Extra.ignore
        orm_mode = True
        from_attributes = True


class Config(BaseConfig):
    json_encoders = JSON_ENCODERS
    extra = Extra.ignore
    orm_mode = True   # v1 版本
    from_attributes = True  # v2 版本


class QueryConfig(BaseConfig):
    json_encoders = JSON_ENCODERS
    extra = Extra.ignore


class IDList(BaseModel):
    id_list: List[str] = []

    # class Config:
    #     json_encoders = JSON_ENCODERS
    #     extra = Extra.ignore

