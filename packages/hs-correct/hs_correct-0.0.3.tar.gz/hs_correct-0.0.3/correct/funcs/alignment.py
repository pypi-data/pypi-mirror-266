"""
位置数据来源：
1.(来源于模板图片)标注数据，原始标注数据格式参考"标注数据详细信息.md"文件，需取出其中的m个：标注点的坐标，对应的答案，以及对应的小题ID
'points':[[x1,y1],...],'answers':['A',...],'dtqMarkIds':[11,11,12...]
2.(来源于模板图片)答题区识别模型，识别模版图片中的答题区，输出n个矩形框坐标信息
3.(来源于笔迹图片)位移算法中的canny算法，识别出笔迹的坐标位置，输出k个矩形框坐标信息
4.(来源于笔迹图片)OCR识别，识别出笔迹的坐标位置和内容，输出t个矩形框坐标信息和内容

输出结果：标注数据中的标注点坐标、对应的答案、OCR识别的文本内容

输入输出数据结构详细格式参考 https://uqwe796vz8c.feishu.cn/wiki/Tye6wMZXyinhJJkU16wcfgj4nWb?from=from_copylink

位置对齐思路：
(此流程之前的流程需先使用位移数据，先对笔迹坐标做一下位移处理，再送入以下流程参与计算，此代码不涉及这部分的处理)
1.以标注数据中的标注点作为核心参考标准
2.先过滤识别的答题区矩形数据，获得对应的正确的答题区矩形框，过滤标准：取包含标注点的分值最高的矩形框
3.使用2步骤中的矩形框，处理OCR识别的矩形框，该合并的合并，该分割的分割，合并或分割后，同时得到合并或分割的文本内容
4.canny的结果怎么使用，目前还想不清楚，暂未使用(将3中的结果与canny算法识别的内容做一个比对，看看差异 ？？？)
"""

import os
import sys
# additional_path = 'd:/MyPythonProjectCode/align_and_review'
# sys.path.append(additional_path)
# print("Current working directory:", os.getcwd())
# print("Python module search path:", sys.path)


from datetime import datetime
import time
import numpy as np
import shapely
from shapely.geometry import Polygon
import json

from correct.logger.logger import Logger

# 日志实例
logger = Logger('correct.funcs.alignment.py')


def alignment(params: dict):
    """
    笔迹对齐
    :param params:  参数 ，参考批阅流程2
        {
            'grade': 年级信息,
            'subject': 学科信息,
            'mark_info': 标注数据，包括[小题ID、题型、标注的位置、标注的答案],
            'dpm_info': 位移数据，包括[缩放比例、旋转角度、X轴位移、Y轴位移],
            'hw_coordinate': 笔记坐标json数据,
            'answering_area_url': 答题区json文件路径,
            'ocr_data': ocr结果，包括[识别的内容、坐标、分值]
        }
    :return: 成功对齐的数据
        [
            {
                // 标注数据点
                "point": (343.77, 443.43),
                // 标准答案
                "answer": "A",
                // 小题id
                "id": 13,
                // 匹配上的ocr识别内容
                "ocr_text": "A"
            },
            ...
        ]
    """
    align_res = position_align(params)

    if 'success' not in align_res or not align_res['success']:
        align_res['success'] = []
    if 'failed' not in align_res or not align_res['failed']:
        align_res['failed'] = []
    logger.warning(f"[alignment]本次标注数据对齐操作"
                   f"预计处理{len(params['mark_data'])}条，"
                   f"成功{len(align_res['success'])}条，"
                   f"失败{len(align_res['failed'])}条")

    if align_res['failed']:
        failed_res = align_res['failed']
        logger.warning(f"[alignment]存在{len(failed_res)}条对齐失败数据，信息如下：")
        for ele in failed_res:
            logger.warning(f"[alignment]"
                           f"id:{ele['mark_data']['id']}、"
                           f"point:{ele['mark_data']['point']}、"
                           f"answer:{ele['mark_data']['answer']}、"
                           f"code:{ele['code']}、"
                           f"message:{ele['message']}"
                           )
    return align_res['success']


def tmp_call():
    timestamp1 = time.time()
    dt1 = datetime.fromtimestamp(timestamp1)
    formatted_dt1 = dt1.strftime("%Y-%m-%d %H:%M:%S")
    print("批改对齐部分开始时间：" + formatted_dt1)
    icount = 20
    quad1_coords = [(0, 0), (0, 2), (2, 2), (2, 0)]
    quad2_coords = [(1, 1), (1, 3), (3, 3), (3, 1)]
    for i in range(icount):
        iou_c1 = bbox_iou_eval(quad1_coords, quad2_coords)
        # print('i_' + str(i) + ':' + str(iou_c1))
        for j in range(icount):
            iou_c3 = bbox_iou_eval(quad1_coords, quad2_coords)
            # print('j_' + str(i) + ':' + str(iou_c3))
            for k in range(icount):
                iou_c5 = bbox_iou_eval(quad1_coords, quad2_coords)
                # print('k_' + str(i) + ':' + str(iou_c5))

    timestamp2 = time.time()
    dt2 = datetime.fromtimestamp(timestamp2)
    formatted_dt2 = dt2.strftime("%Y-%m-%d %H:%M:%S")
    print("批改对齐部分结束时间：" + formatted_dt2)

    delta_time = timestamp2 - timestamp1
    print("批改对齐部分总耗时: {:.2f}分钟".format(delta_time / 60))


# 定义一个函数用来判断某个点是否在矩形框内
def point_match_area(point_co, box_co):
    x1, y1, x2, y2 = find_minmax_xy_of_quadrilateral(box_co)
    px, py = point_co

    # 检查点的 x 坐标是否在矩形框的 x 坐标范围内
    if x1 <= px <= x2:
        # 检查点的 y 坐标是否在矩形框的 y 坐标范围内
        if y1 <= py <= y2:
            return True
    return False


# 定义一个函数来找到四边形在X轴上的最小值
# def min_x_of_quad(quad):
#     return min(x for x, _ in quad)

# 定义一个函数来找到四边形的xmin,ymin,xmax,ymax
def find_minmax_xy_of_quadrilateral(quad):
    """
    找到四边形在XY轴上的最小值最大值。

    :param quad: 四边形的顶点坐标列表，每个顶点是一个 (x, y) 元组
    :return: 四边形在X轴上的最小值
    """
    # 确保传入的是一个包含四个顶点的列表
    if len(quad) != 4:
        raise ValueError(
            "The input must be a list of four (x, y) coordinates representing the quadrilateral's vertices.")

    # 提取所有顶点的X坐标
    x_coords = [pt[0] for pt in quad]

    # 提取所有顶点的Y坐标
    y_coords = [pt[1] for pt in quad]

    # 找到X坐标中的最小值
    min_x = min(x_coords)

    # 找到X坐标中的最大值
    max_x = max(x_coords)

    # 找到Y坐标中的最小值
    min_y = min(y_coords)

    # 找到Y坐标中的最大值
    max_y = max(y_coords)

    mm_data = [min_x, min_y, max_x, max_y]
    return mm_data


# 定义一个函数用来计算两个四边形的交集面积/并集面积/交并比IoU三个值
def bbox_iou_eval(box1, box2):
    box1 = np.array(box1).reshape(4, 2)
    poly1 = Polygon(box1).convex_hull  # POLYGON ((0 0, 0 2, 2 2, 2 0, 0 0))
    # print(type(mapping(poly1)['coordinates'])) # (((0.0, 0.0), (0.0, 2.0), (2.0, 2.0), (2.0, 0.0), (0.0, 0.0)),)
    # poly_arr = np.array(poly1)

    box2 = np.array(box2).reshape(4, 2)
    poly2 = Polygon(box2).convex_hull

    if not poly1.intersects(poly2):  # 如果两四边形不相交
        iou = 0
    else:
        try:
            inter_area = poly1.intersection(poly2).area  # 相交面积
            union_area = poly1.area + poly2.area - inter_area
            iou = float(inter_area) / (union_area)
        except shapely.geos.TopologicalError:
            print('shapely.geos.TopologicalError occured, iou set to 0')
            iou = 0
    return iou


def polygon_center(A, B, C, D):
    """
    计算四边形的中心点坐标。

    :param A: 第一个顶点坐标 (x1, y1)
    :param B: 第二个顶点坐标 (x2, y2)
    :param C: 第三个顶点坐标 (x3, y3)
    :param D: 第四个顶点坐标 (x4, y4)
    :return: 四边形的中心点坐标 (x, y)
    """
    # 计算四边形的最小凸包矩形的中心点
    # 这里我们使用四个顶点的坐标来确定矩形的边界
    min_x = min(A[0], B[0], C[0], D[0])
    max_x = max(A[0], B[0], C[0], D[0])
    min_y = min(A[1], B[1], C[1], D[1])
    max_y = max(A[1], B[1], C[1], D[1])

    # 计算矩形的中心点坐标
    center_x = (min_x + max_x) / 2
    center_y = (min_y + max_y) / 2

    return (center_x, center_y)


# 定义一个函数,判断某个OCR框，是否是目标框要找的match框
def is_effective_ocrbox(t_box, s_box):
    s_center = polygon_center(s_box[0], s_box[1], s_box[2], s_box[3])
    t_center = polygon_center(t_box[0], t_box[1], t_box[2], t_box[3])
    if abs(s_center[1] - t_center[1]) > 25:  # 计算此时的位置关系为竖向还是横向，如果两个矩形框相交不多且y轴中心点的距离大于25，则认为它俩是竖向分布，抛弃不要
        return False
    else:
        return True


def position_align(alldata):
    print("alldata:")
    print(alldata)
    markdata = alldata["mark_data"]
    areadata = alldata["answering_area_data"]
    ocrdata = alldata["ocr_data"]
    cannydata = alldata["hw_coordinate_data"]

    f_sindata = {"point": [], "answer": '', "id": -9999999, "parent_id": -9999999, "ocr_text": '', "code": 0, "message": ''}

    finaldata = []  # 保存最终输出的结果
    # 1.遍历标注数据中的每一个点
    for mark in markdata:
        point_coordinate = mark["point"]
        align_result_code = 0
        align_error_instruction = ""
        # 2.遍历答题区矩形框，匹配标注点对应的答题区矩形框
        # 此处可能存在一个问题，即某些特殊题型，模型无法识别它的答题区域，然后就导致一些标注点找不到对应的答题区矩形框，以后怎么优化？？？
        match_area_box = []
        match_area_score = 0
        for area in areadata:
            if point_match_area(point_coordinate, area["points"]):
                if match_area_score == 0:  # 初始值，表明该标注点是第一次匹配答题区矩形框
                    match_area_box = area["points"]
                    match_area_score = area["score"]
                else:  # 该标注点不是第一次匹配答题区矩形框，取分值高的
                    if area["score"] > match_area_score:  # 遇到了分值更高的框，更新数据
                        match_area_box = area["points"]
                        match_area_score = area["score"]

        if match_area_score == 0:  # 如果最终匹配到的分值为0，即初始值，表明未匹配到任何答题区矩形框，不用再走后面的流程；以后有没有方案可以做？？？
            if len(areadata) == 0:
                align_error_instruction = "areadata is empty, no any area box"
            else:
                align_result_code = -1
                align_error_instruction = "this mark point don't find match area box"

            f_sindata["point"] = point_coordinate
            f_sindata["answer"] = mark["answer"]
            f_sindata["id"] = mark["id"]
            f_sindata["parent_id"] = mark["parent_id"]
            f_sindata["ocr_text"] = ''
            f_sindata["code"] = align_result_code
            f_sindata["message"] = align_error_instruction
            finaldata.append(f_sindata)
            continue

        # 3.遍历OCR识别的目标框，获得对应的文本内容
        match_ocr_datalist = []
        for ocr in ocrdata:
            iou_c = bbox_iou_eval(match_area_box, ocr["points"])
            if iou_c > 0:  # 交集的面积大于0，表明有交集
                if iou_c < 0.1:  # 交并比低于0.1，则认为两个矩形的重叠区域不多，阈值可能不合适，后期需要改
                    if is_effective_ocrbox(match_area_box, ocr["points"]):  # 说明两个矩形框是横向分布，该矩形框与答题区矩形框对应，留下
                        tempdata = {"minx": 999999999, "text": ''}
                        tempdata["minx"] = find_minmax_xy_of_quadrilateral(ocr["points"])[0]  # 保存该矩形框坐标在X轴上的最小值
                        tempdata["text"] = ocr["content"]
                        match_ocr_datalist.append(tempdata)
                else:
                    tempdata = {"minx": 999999999, "text": ''}
                    tempdata["minx"] = find_minmax_xy_of_quadrilateral(ocr["points"])[0]  # 保存该矩形框坐标在X轴上的最小值
                    tempdata["text"] = ocr["content"]
                    match_ocr_datalist.append(tempdata)

        if len(match_ocr_datalist) == 0:  # 如果最终匹配到的ocr框为0个，不用再走后面的流程；
            align_result_code = -2
            align_error_instruction = "this mark point don't find match ocr box"
            f_sindata["point"] = point_coordinate
            f_sindata["answer"] = mark["answer"]
            f_sindata["id"] = mark["id"]
            f_sindata["parent_id"] = mark["parent_id"]
            f_sindata["ocr_text"] = ''
            f_sindata["code"] = align_result_code
            f_sindata["message"] = align_error_instruction
            finaldata.append(f_sindata)
            continue

        # 4.将找到的OCR矩形框，按照X轴方向进行排序，然后合并内容
        sorted_ocrboxes = sorted(match_ocr_datalist, key=lambda x: x["minx"], reverse=True)
        # 使用列表推导式根据新的排序输出 'name' 键的所有值
        sorted_ocr_text = [person["text"] for person in sorted_ocrboxes]
        print(sorted_ocr_text)  # 输出排序后的 'ocr_text' 值列表
        join_ocr_text = ''.join(sorted_ocr_text)  # 将这些text拼接起来，即为答题区识别框对应的笔迹的书写内容

        align_result_code = 1
        align_error_instruction = "success"

        f_sindata["point"] = point_coordinate
        f_sindata["answer"] = mark["answer"]
        f_sindata["id"] = mark["id"]
        f_sindata["parent_id"] = mark["parent_id"]
        f_sindata["ocr_text"] = join_ocr_text
        f_sindata["code"] = align_result_code
        f_sindata["message"] = align_error_instruction
        print("f_sindata:")
        print(f_sindata)
        finaldata.append(f_sindata)

    # 5.整理输出数据
    successlist = []
    failedlist = []
    for sindata in finaldata:
        if sindata["code"] == 1:
            successdata = {"point": sindata["point"], "answer": sindata["answer"], "id": sindata["id"],
                           "parent_id": sindata["parent_id"], "ocr_text": sindata["ocr_text"]}
            successlist.append(successdata)
        else:
            data_mark = {"point": sindata["point"], "answer": sindata["answer"], "id": sindata["id"], "parent_id": sindata["parent_id"]}
            faileddata = {"code": sindata["code"], "message": sindata["message"], "mark_data": data_mark}
            failedlist.append(faileddata)

    alignoutput = {"success": successlist, "failed": failedlist}
    return alignoutput


# if __name__ == "__main__":
#     #alignment_sample_data.json数据用来测试
#     labeledfile = '../data_demo/alignment_sample_data.json'
#     f = open(labeledfile, 'r')
#     labeledcontent = f.read()
#     f.close()
#     labeled_json = json.loads(labeledcontent)
#     allpositiondata = labeled_json
#     print("allpositiondata:")
#     print(allpositiondata)
#     finalresult = position_align(allpositiondata)
#     print("finalresult:")
#     print(finalresult)