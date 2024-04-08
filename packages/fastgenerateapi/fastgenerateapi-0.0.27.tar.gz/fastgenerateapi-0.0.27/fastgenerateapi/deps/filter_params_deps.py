from typing import Type, Union, Any

from fastapi import Depends
from tortoise import Model

from fastgenerateapi.controller.filter_controller import BaseFilter
from fastgenerateapi.schemas_factory.filter_schema_factory import filter_schema_factory


def filter_params_deps(model_class: Type[Model], fields: list[str, tuple[str, Type], BaseFilter] = None):
    """
        生成filter依赖
    """
    filter_params_model = filter_schema_factory(model_class, fields)

    def filter_query(filter_params: filter_params_model = Depends(filter_params_model)) -> dict[str, Any]:
        """
            filter 筛选字段依赖
        :param filter_params:
        :return:
        """
        result = filter_params.dict(exclude_none=True)
        return result

    return filter_query
