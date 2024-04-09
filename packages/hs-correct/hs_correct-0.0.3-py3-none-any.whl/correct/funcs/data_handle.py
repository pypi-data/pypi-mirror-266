"""
数据校验、解析和预处理
"""
from correct.exception.correct_exception import CorrectException
from correct.tools.rectangle_handle import RectTransform
from correct.logger.logger import Logger

# 日志实例
logger = Logger('correct.funcs.data_handle.py')


def check_params(params: dict):
    if not params or type(params) is not dict:
        raise CorrectException.ud_correct_exception('入参为空或类型有误')

    if "grade_id" not in params:
        raise CorrectException.ud_correct_exception('请输入年级信息')
    else:
        grade_id = params['grade_id']
    if "subject_id" not in params:

        raise CorrectException.ud_correct_exception('请输入学科信息')
    else:
        subject_id = params['subject_id']

    if "mark_data" not in params or not params['mark_data']:
        raise CorrectException.ud_correct_exception('请输入标注数据')
    else:
        mark_data = parse_mark_data(params['mark_data'])

    if "dpm_data" not in params or not params['dpm_data']:
        raise CorrectException.ud_correct_exception('请输入位移数据')
    else:
        dpm_data = parse_dpm_data(params['dpm_data'])

    if "hw_coordinate_data" not in params or not params['hw_coordinate_data']:
        raise CorrectException.ud_correct_exception('请输入笔记坐标数据')
    else:
        hw_coordinate_data = parse_hw_coordinate_data(params['hw_coordinate_data'])
        # 笔记坐标数据（暂时不用入参hw_coordinate_data，而是使用这里位移数据中顺带的已经解析好的answer_condition）
        # hw_coordinate_data = parse_hw_coordinate_data(params['dpm_data'])

    if "answering_area_data" not in params or not params['answering_area_data']:
        raise CorrectException.ud_correct_exception('请输入答题区数据')
    else:
        answering_area_data = parse_answering_area_data(params['answering_area_data'])

    if "ocr_data" not in params or not params['ocr_data']:
        raise CorrectException.ud_correct_exception('请输入ocr结果数据')
    else:
        ocr_data = parse_ocr_data(params['ocr_data'])

    return grade_id, subject_id, mark_data, dpm_data, hw_coordinate_data, answering_area_data, ocr_data


def parse_mark_data(raw_mark_info: dict):
    """
    从标注数据中解析出对齐需要的数据
    格式：
    [
        {
            'point': (333,455),
            'answer': 'A',
            'id': 2,
            // 所属大题id
            'parent_id': 5
        },
        ...
    ]
    :param raw_mark_info: 标注数据
    :return: list
    """
    res = []
    for ele in raw_mark_info:
        parent_id = ele['id']
        if 'isDtqInteractionVo' not in ele or not ele['isDtqInteractionVo']:
            logger.error(f"[parse_mark_data]id为{parent_id}的大题数据中未解析到小题数据，该大题将跳过批阅处理")
            continue
        else:
            one_group = [
                {
                    'id': ele2['dtqId'],
                    'point': (ele2['dtqX'], ele2['dtqY']),
                    'answer': ele2['dtqAnswer'],
                    'parent_id': parent_id
                } for ele2 in ele['isDtqInteractionVo']]
            res.extend(one_group)
    return res


def parse_dpm_data(raw_dpm_data: dict):
    """
    解析出需要的位移数据
    :param raw_dpm_data: 位移数据
    :return: dict
    """
    return {
        "scale": raw_dpm_data['scale'],
        "angle": raw_dpm_data['angle'],
        "offset_x": raw_dpm_data['offset_x'],
        "offset_y": raw_dpm_data['offset_y']
    }


def parse_hw_coordinate_data(raw_hw_coordinate_data: dict):
    """
    从笔迹坐标数据中解析出对齐需要的数据
    格式：[[x,x,...],...]
    :param raw_hw_coordinate_data: 笔迹坐标
    :return: list
    """
    # if "answer_condition" not in raw_hw_coordinate_data or not raw_hw_coordinate_data['answer_condition']:
    #     raise CorrectException.ud_correct_exception("未从位移数据中解析到笔迹坐标数据")
    # tmp_data = raw_hw_coordinate_data['answer_condition']
    return [
        {
            "points": [
                (ele[0], ele[1]),
                (ele[2], ele[1]),
                (ele[2], ele[3]),
                (ele[0], ele[3]),
            ],
            "sort": ele[4]
        } for ele in raw_hw_coordinate_data
    ]


def parse_answering_area_data(raw_answering_area_data: dict):
    """
    从答题区数据中解析出对齐需要的数据
    :param raw_answering_area_data: 答题区数据
    :return: list
    """
    return [
        {
            "points": [
                (ele[0], ele[1]),
                (ele[2], ele[1]),
                (ele[2], ele[3]),
                (ele[0], ele[3]),
            ],
            "sort": ele[5],
            "score": ele[4]
        } for ele in raw_answering_area_data['all']
    ]


def parse_ocr_data(raw_ocr_data: dict):
    """
    从ocr识别结果数据中解析出对齐需要的数据
    格式：
    [{},...]
    :param raw_ocr_data: ocr识别结果
    :return: list
    """
    return [
        {
            "points": [
                tuple(ele['points'][0]),
                tuple(ele['points'][1]),
                tuple(ele['points'][2]),
                tuple(ele['points'][3]),
            ],
            "score": ele['reliability'],
            "content": ele['transcription']
        } for ele in raw_ocr_data['rec_res'][0]['rec_content']
    ]


def dpm_the_data(target_data, dpm_data):
    """
    对数据进行位移
    :param target_data: 要处理的数据，必须包含名为"points"的key，该key格式为[(x1, y1), (x2, y2), (x3, y3), (x4, y4)]
    :param dpm_data: 位移数据
    :return:
    """
    # 位移参数
    scale = dpm_data['scale']
    angle = dpm_data['angle']
    offset_x = dpm_data['offset_x']
    offset_y = dpm_data['offset_y']

    for ele in target_data:
        ele['points'] = RectTransform.scale(ele['points'], scale, scale)
        ele['points'] = RectTransform.translate(ele['points'], offset_x, offset_y)
        ele['points'] = RectTransform.rotate(ele['points'], -angle)
