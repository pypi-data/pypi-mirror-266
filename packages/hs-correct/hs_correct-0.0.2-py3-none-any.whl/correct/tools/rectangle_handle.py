"""
处理矩形
"""
import math


class RectTransform:
    @staticmethod
    def translate(rect, dx, dy):
        """  
        平移矩形
        :param rect: 矩形的顶点列表，形如 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]  
        :param dx: x轴平移距离，正右负左
        :param dy: y轴平移距离，正上负下
        :return: 平移后的矩形顶点列表  
        """
        return [(x + dx, y + dy) for x, y in rect]

    @staticmethod
    def scale(rect, scale_x, scale_y):
        """  
        伸缩矩形
        :param rect: 矩形的顶点列表，形如 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]  
        :param scale_x: x轴伸缩比例，>1放大<1缩小
        :param scale_y: y轴伸缩比例，>1放大<1缩小
        :return: 伸缩后的矩形顶点列表  
        """
        return [(x * scale_x, y * scale_y) for x, y in rect]

    @staticmethod
    def rotate(rect, angle_degrees, center=None):
        """
        旋转矩形
        :param rect: 矩形的顶点列表，形如 [(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
        :param angle_degrees: 旋转角度（度），正逆时针；负顺时针
        :param center: 旋转中心，默认为矩形的中心点。如果提供，应为形如 (cx, cy) 的元组。
        :return: 旋转后的矩形顶点列表（可能是一个四边形）
        """
        # 将角度转换为弧度
        angle_radians = math.radians(angle_degrees)

        # 如果未指定中心，则计算矩形的中心点
        if center is None:
            # 计算矩形的边界
            x_min, y_min = min(x for x, _ in rect), min(y for _, y in rect)
            x_max, y_max = max(x for x, _ in rect), max(y for _, y in rect)
            # 计算中心点
            center_x = (x_min + x_max) / 2
            center_y = (y_min + y_max) / 2
            center = (center_x, center_y)

            # 旋转矩阵
        cos_theta = math.cos(angle_radians)
        sin_theta = math.sin(angle_radians)

        # 旋转每个顶点
        rotated_rect = []
        for x, y in rect:
            # 顶点相对于中心点的偏移量
            dx = x - center[0]
            dy = y - center[1]
            # 旋转偏移量
            dx_rotated = dx * cos_theta - dy * sin_theta
            dy_rotated = dx * sin_theta + dy * cos_theta
            # 将旋转后的偏移量加回到中心点上
            x_rotated = dx_rotated + center[0]
            y_rotated = dy_rotated + center[1]
            rotated_rect.append((x_rotated, y_rotated))

        return rotated_rect
