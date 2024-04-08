from typing import Type, Union

from fastapi import Query
from fastgenerateapi.pydantic_utils.base_model import QueryConfig
from pydantic import BaseModel, create_model
from pydantic.fields import FieldInfo

from fastgenerateapi.api_view.mixin.dbmodel_mixin import DBModelMixin
from fastgenerateapi.controller.filter_controller import BaseFilter
from tortoise import Model


def filter_schema_factory(model_class: Type[Model], fields: list[str, tuple[str, Type], BaseFilter] = None):
    """
        generate filter schema
    """
    model_fields = {}

    for field_info in fields or []:
        if not isinstance(field_info, BaseFilter):
            field_info = BaseFilter(field_info)
        f = field_info.filter_field
        t = field_info.field_type

        model_fields.update({
            f: (
                Union[t, str],
                FieldInfo(
                    title=f"{f}",
                    default=Query(""),
                    description=f"{DBModelMixin.get_field_description(model_class, field_info.model_field)}"
                ))
        })

    filter_params_model: Type[BaseModel] = create_model(__model_name="CommonFilterParams", **model_fields, __config__=QueryConfig)

    return filter_params_model



