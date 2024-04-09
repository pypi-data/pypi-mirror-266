"""
处理点
"""
import math


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def __repr__(self):
        return f"Point({self.x}, {self.y})"


def translate(point, delta_x, delta_y):
    """
    平移函数
    :param point: Point
    :param delta_x: x轴位移量。正右负左
    :param delta_y: y轴位移量。正上负下
    :return: Point
    """
    return Point(point.x + delta_x, point.y + delta_y)


def scale(point, scale_factor):
    """
    伸缩函数
    :param point: Point
    :param scale_factor: 伸缩量。>1放大，<1缩小
    :return: Point
    """
    return Point(point.x * scale_factor, point.y * scale_factor)


def rotate(point, theta):
    """
    旋转函数（以原点为中心，正值表示逆时针旋转，负值表示顺时针旋转）
    :param point: Point
    :param theta: 旋转角度。正值逆时针，负值顺时针
    :return: Point
    """
    cos_theta = math.cos(theta)
    sin_theta = math.sin(theta)
    x = point.x * cos_theta - point.y * sin_theta
    y = point.x * sin_theta + point.y * cos_theta
    return Point(x, y)


# 示例
if __name__ == "__main__":
    # 创建一个点
    p = Point(1.0, 2.0)
    print("原始点:", p)

    # 平移点
    translated_p = translate(p, 3, 4)
    print("平移后的点:", translated_p)

    # 伸缩点
    scaled_p = scale(p, 2)
    print("伸缩后的点:", scaled_p)

    # 旋转点（例如，旋转90度）
    rotated_p = rotate(p, math.pi / 2)
    print("旋转后的点:", rotated_p)
