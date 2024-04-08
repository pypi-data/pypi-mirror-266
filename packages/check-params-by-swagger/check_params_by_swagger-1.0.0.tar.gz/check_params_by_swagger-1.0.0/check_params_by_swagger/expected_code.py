# -*- coding:UTF-8 -*-

"""
 @ProjectName  : SwaggerCheck 
 @FileName     : expected_code
 @Description  : 期望结果
 @Time         : 2024/4/3 19:26
 @Author       : Qredsun
 """


# 必填参数缺失时，错误码
class NecessaryParamMissExpected():
    NOTE = '必填参数校验'
    CODES = ["BASE-0002", ]


# 参数类型错误时，错误码
class ParamTypeErrorExpected():
    NOTE = '参数类型校验'
    CODES = ["BASE-0002", ]


# 参数类型错误时，错误码
class ParamValueErrorExpected():
    NOTE = '参数范围校验'
    CODES = ["BASE-0002", ]