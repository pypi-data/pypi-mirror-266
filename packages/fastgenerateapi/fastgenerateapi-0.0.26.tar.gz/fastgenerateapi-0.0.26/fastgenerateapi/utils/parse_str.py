from typing import Union

from fastgenerateapi.settings.register_settings import settings


def parse_str_to_bool(val: Union[int, str, bool, None]):
    """
    解析字符串到布尔值
    """
    if type(val) == bool:
        return val
    elif type(val) == int:
        return val != 0
    elif type(val) == str:
        if val.upper() in ("1", "ON", "TRUE"):
            return True
        elif val.upper() in ("0", "OFF", "FALSE"):
            return False
    return settings.app_settings.DEFAULT_WHETHER_PAGE


def parse_str_to_int(val: Union[int, str, None]):
    """
    解析字符串到数值
    """
    if type(val) == int:
        return val
    elif type(val) == str:
        try:
            val = int(val)
        except Exception as e:
            val = 0
        return val

    return 0

