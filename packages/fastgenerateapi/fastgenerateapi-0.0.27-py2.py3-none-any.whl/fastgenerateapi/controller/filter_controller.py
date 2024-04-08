from typing import Union, Any

from tortoise.expressions import Q
from tortoise.queryset import QuerySet

from fastgenerateapi.settings.register_settings import settings


class BaseFilter:
    """
        BaseFilter
    """

    def __init__(self, filter_str: Union[str, tuple]):
        """
        :param filter_str:  Union[str, tuple]
        example： name__contains or (create_at__gt, datetime) or (create_at__gt, datetime, create_time)
        """
        field_type = str
        model_field = filter_str
        filter_field = filter_str
        if isinstance(filter_str, str):
            if settings.app_settings.FILTER_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE and "__" in filter_str:
                filter_field = filter_str.replace("__", "_")
        # 判断filter表达式的类型
        if isinstance(filter_str, tuple):
            model_field = filter_str[0]
            if len(filter_str) == 2:
                if type(filter_str[1]) == type:
                    field_type = filter_str[1]
                    if settings.app_settings.FILTER_UNDERLINE_WHETHER_DOUBLE_TO_SINGLE and "__" in filter_str:
                        filter_field = model_field.replace("__", "_")
                    else:
                        filter_field = model_field
                else:
                    filter_field = filter_str[1]
            elif len(filter_str) > 2:
                if type(filter_str[1]) == type:
                    field_type = filter_str[1]
                    filter_field = filter_str[2]
                else:
                    field_type = filter_str[2]
                    filter_field = filter_str[1]

        self.model_field = model_field
        self.filter_field = filter_field
        self.field_type = field_type

    def generate_q(self, value: Union[str, list, bool]) -> Q:
        """
            生成Q查询对象
        :param value:
        :return:
        """
        if isinstance(value, str):
            if value.upper() in ["NONE", "NULL", "NIL", "0"]:
                return eval(f"Q({self.model_field}={None})")
            return eval(f"Q({self.model_field}='{value}')")
        return eval(f"Q({self.model_field}={value})")

    def query(self, queryset: QuerySet, value: Union[str, list, bool]) -> QuerySet:
        """
            do query action
        :param queryset:
        :param value:
        :return:
        """
        queryset = queryset.filter(self.generate_q(value=value))
        return queryset


class FilterController:
    """
        FilterController
    """

    def __init__(self, filters: list[BaseFilter]):
        self.filters = filters
        self.filter_map: dict[str, BaseFilter] = {}
        for f in self.filters:
            self.filter_map[f.filter_field] = f

    def query(self, queryset: QuerySet, values: dict[str, Any]) -> QuerySet:
        """
            do query action
        :param queryset:
        :param values:
        :return:
        """
        for k in values:
            f = self.filter_map.get(k, None)
            v = values[k]
            if f is not None and (isinstance(v, bool) or v):
                queryset = f.query(queryset=queryset, value=v)

        return queryset

    def is_empty(self) -> bool:
        return len(self.filters) == 0













