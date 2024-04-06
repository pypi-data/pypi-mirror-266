from typing import List

from pydantic import BaseModel as PydanticBaseModel, Extra, BaseConfig

from fastgenerateapi.pydantic_utils.json_encoders import JSON_ENCODERS


class BaseModel(PydanticBaseModel):
    class Config:
        json_encoders = JSON_ENCODERS
        extra = Extra.ignore
        orm_mode = True


class Config(BaseConfig):
    json_encoders = JSON_ENCODERS
    extra = Extra.ignore
    orm_mode = True


class QueryConfig(BaseConfig):
    json_encoders = JSON_ENCODERS
    extra = Extra.ignore


class IDList(BaseModel):
    id_list: List[str] = []

    # class Config:
    #     json_encoders = JSON_ENCODERS
    #     extra = Extra.ignore

