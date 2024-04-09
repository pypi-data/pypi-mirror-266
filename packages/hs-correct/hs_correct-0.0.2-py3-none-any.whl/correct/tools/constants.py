"""
常量
"""


class Constant:
    def __setattr__(self, key, value):
        if key in self.__dict__:
            raise AttributeError("Cannot modify the value of a constant")
        else:
            self.__dict__[key] = value


constants = Constant()

constants.NUM_ZERO = 0
constants.NUM_ONE = 1
constants.NUM_TWO = 2
constants.NUM_THREE = 3
constants.NUM_FOUR = 4

constants.STR_SLASH = '/'
constants.STR_SIMPLE_DATE = '%y-%m-%d'
