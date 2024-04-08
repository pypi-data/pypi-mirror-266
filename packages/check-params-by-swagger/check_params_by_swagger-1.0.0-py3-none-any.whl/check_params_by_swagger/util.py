# -*- coding:UTF-8 -*-

"""
 @ProjectName  : SwaggerCheck 
 @FileName     : util
 @Description  : 
 @Time         : 2024/4/3 19:27
 @Author       : Qredsun
 """
import random
import string
from datetime import datetime
from datetime import timedelta


class RequiredTree():
    def __init__(self, borthers: list, children, enums = None):
        self._brothers = borthers
        self._children = children
        self._enums = enums

    @property
    def brothers(self) -> list:
        # 必填参数
        return self._brothers

    @property
    def children(self):
        return self._children

    @property
    def enum(self):
        # 枚举值
        return self._enums


# 生成随机字符串
def random_string(length: int) -> str:
    return ''.join(random.choices(string.ascii_letters + string.digits, k=length))


# 根据指定日期、推迟时间，生成指定时间格式的时间
def time_delta_by_days(time_str, delta, time_format):
    temp_time = datetime.strptime(time_str, time_format)
    temp_time_str = (temp_time + timedelta(days=delta)).strftime(time_format)
    return temp_time_str

