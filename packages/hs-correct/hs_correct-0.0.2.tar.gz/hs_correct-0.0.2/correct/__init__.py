"""
对齐及批改函数调用入口
zgl/24.03.26
"""
import time

from correct.funcs.data_handle import check_params, dpm_the_data
from correct.funcs.alignment import alignment, tmp_call
from correct.funcs.correction import correct, tmp_res
from correct.tools.rectangle_handle import RectTransform
from correct.response.response import Response
from correct.response.response_code import (RES_1002_SYS_ERR)
from correct.exception.correct_exception import CorrectException
from correct.logger.logger import Logger

# 日志实例
logger = Logger('correct.__init__.py')


def tmp_correct(params: dict):
    """
    批阅入口，入参结构如下：
    :param params:
    {
        "grade_id": 年级id,
        "subject_id": 学科id,
        "mark_data": 标注数据，包括[小题ID、题型、标注的位置、标注的答案],
        "dpm_data": 位移数据，包括[缩放比例、旋转角度、X轴位移、Y轴位移],
        "hw_coordinate_data": 笔记坐标json数据,
        "answering_area_data": 答题区json数据,
        "ocr_data": ocr结果，包括[识别的内容、坐标、分值]
    }
    :return:
    """
    # 校验并解析入参中需要的内容
    (grade_id, subject_id, mark_data, dpm_data, hw_coordinate_data, answering_area_data, ocr_data) \
        = check_params(params)

    # 根据位移数据处理笔迹坐标和ocr结果中的坐标
    dpm_the_data(hw_coordinate_data, dpm_data)
    dpm_the_data(ocr_data, dpm_data)

    # 对齐分析，找到 [标注数据 <-> ocr结果] 的对应关系
    alignment_res = alignment({
        "mark_data": mark_data,
        "answering_area_data": answering_area_data,
        "hw_coordinate_data": hw_coordinate_data,
        "ocr_data": ocr_data
    })

    # 按照[标注数据 <-> ocr结果]计算批改结果
    correct_res = correct(alignment_res)

    return correct_res


def correct_with_res_code(param: dict):
    try:

        # 记录开始时间
        start_time = time.perf_counter()

        res = tmp_correct(param)

        # 记录结束时间
        end_time = time.perf_counter()
        # 计算时长
        duration = end_time - start_time
        logger.info(f"[correct_with_res_code]本次调用耗时{duration}秒")

        return Response.success(res).to_res_dict()
    except CorrectException as e:
        logger.exception(f"[correct]批改流程异常：{e}")
        return Response.failure_code((e.code, e.message)).to_res_dict()
    except Exception as e:
        logger.exception(f"[correct]系统异常：{e}")
        return Response.failure_code(RES_1002_SYS_ERR).to_res_dict()


def do_correct(params: dict):
    """
    批阅入口，入参结构如下：
    :param params:
    {
        "grade_id": 年级id,
        "subject_id": 学科id,
        "mark_data": 标注数据，包括[小题ID、题型、标注的位置、标注的答案],
        "dpm_data": 位移数据，包括[缩放比例、旋转角度、X轴位移、Y轴位移],
        "hw_coordinate_data": 笔记坐标json数据,
        "answering_area_data": 答题区json数据,
        "ocr_data": ocr结果，包括[识别的内容、坐标、分值]
    }
    详细结构格式见.data_demo.request.json
    :return: dict。结构格式见.data_demo.response.json
    """
    # 解析参数
    (grade_id, subject_id, mark_data, dpm_data, hw_coordinate_data, answering_area_data, ocr_data) \
        = check_params(params)

    # 对齐
    tmp_call()

    # 延时2秒模拟程序执行
    time.sleep(2)

    # 批改
    return tmp_res(mark_data)
