"""
批阅模块异常类
"""
from correct.response.response_code import (RES_1003_PARAM_ERR)


class CorrectException(Exception):
    def __init__(self, code, message):
        self.code = code
        self.message = message
        super().__init__(self.code, self.message)

    @classmethod
    def ud_correct_exception(cls, msg: str):
        return cls(RES_1003_PARAM_ERR[0], msg)

    @classmethod
    def any_correct_exception(cls, res_code: tuple):
        return cls(res_code[0], res_code[1])

    def __str__(self):
        return f"CorrectException: {self.code, self.message}"
