import time
from datetime import datetime

from correct.response.response_code import (RES_200_OK, RES_1003_PARAM_ERR)


class Response:
    def __init__(self, code: int, message: str, data: any = None, timestamp: float = None):
        self.code = code
        self.message = message
        self.data = data if data is not None else {}
        self.timestamp = timestamp if timestamp is not None else time.time()

    def to_res_dict(self):
        """将HTTPResponse对象转换为字典形式"""
        return {
            'code': self.code,
            'message': self.message,
            'data': self.data,
            'timestamp': self.timestamp,
            # 'timestamp_formatted': datetime.fromtimestamp(self.timestamp).isoformat(),  # 可选：格式化时间戳为ISO格式字符串
        }

    @classmethod
    def success(cls, data: any = None):
        return cls(RES_200_OK[0], RES_200_OK[1], data, time.time())

    @classmethod
    def failure(cls, msg: str):
        return cls(RES_1003_PARAM_ERR[0], msg, None, time.time())

    @classmethod
    def failure_code(cls, res_code: tuple):
        return cls(res_code[0], res_code[1], None, time.time())
