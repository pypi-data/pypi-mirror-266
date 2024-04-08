# 计算机登录用户: jk
# 系统日期: 2023/10/31 14:13
# 项目名称: chipeak_cv_data_tool
# 开发者: zhanyong
import os.path
import json
from pathlib import Path
from ccdt.dataset import *


class BaseSys(BaseLabelme):
    def __init__(self, *args, **kwargs):
        self.label_name = args[1].label_name  # 获取自定义模型标签名称
        self.background = args[1].background  # 获取是否保存json，默认false
        # 在这里定义labelme数据结构格式初始化
        super(BaseSys, self).__init__(*args, **kwargs)

    def sys2labelme(self):
        sys_to_labelme = list()
        for dataset in self.datasets:
            # print(dataset)
            # obj_path = Path(dataset.get("full_path"))
            # json_file = obj_path.stem + '.json'
            # 拼接json路径，读取json文件，封装labelme_info对象
            # dataset.get("full_path")
            # original_json_path = os.path.join(obj_path.parent, json_file)
            # relative_path = Path('../', '00.images', dataset.get('image_file'))
            # image_dir = Path(dataset.get('image_dir'), "00.images")
            with open(dataset.get("original_json_path"), 'r', encoding='UTF-8') as labelme_fp:
                content = json.load(labelme_fp)
                labelme_info = self.analysis_json(content)  # 解析json格式内容，返回labelme格式
                # 更新labelme的字典结构内容
                labelme_info.update({'imagePath': str(dataset.get("relative_path"))})
                labelme_info.update({'imageHeight': dataset.get('image_height')})
                labelme_info.update({'imageWidth': dataset.get('image_width')})
                labelme_info.update({'md5Value': dataset.get('md5_value')})
                # 更新保存labelme的字典结构内容
                # dataset.update({'relative_path': dataset.get("relative_path")})
                dataset.update({'labelme_info': labelme_info})
                # dataset.update({'image_dir': image_dir})
                dataset.update({'background': self.background})
            sys_to_labelme.append(dataset)
        self.save_labelme(sys_to_labelme, self.output_dir, None)  # self.output_dir为空字符串也是可以的

    def analysis_json(self, content):
        # 定义labelme数据结构
        labelme_data = dict(
            version='4.5.14',
            flags={},
            shapes=[],
            imagePath=None,
            imageData=None,
            imageHeight=None,
            imageWidth=None,
            md5Value=None
        )
        for key, value in content.items():
            if key == "alarm_data":  # 目标检测框
                # 存在的隐患，alarm_data这个字典中，针对多个目标是什么结构目前不清楚，以下逻辑，有且只有一个目标框的情况
                lt_x = content.get("alarm_data").get("rectangle").get('lt_x')
                lt_y = content.get("alarm_data").get("rectangle").get('lt_y')
                rb_x = content.get("alarm_data").get("rectangle").get('rb_x')
                rb_y = content.get("alarm_data").get("rectangle").get('rb_y')
                message = content.get("alarm_data").get("message")
                confidence = str(content.get("alarm_data").get("confidence"))
                text = message + " 阈值" + confidence  # 车牌和阈值拼接
                points = [[lt_x, lt_y], [rb_x, rb_y]]  # 坐标点计算，目前使用左上角的点和右下角的点计算
                shape = {"label": self.label_name, "points": points, "group_id": None, "shape_type": "rectangle", "flags": {}, 'text': text}
                labelme_data.get('shapes').append(shape)
            if key == "vertex_data" and value is not None:  # 多边形坐标点，在多边形不为空的前提下进行
                for polygon_key, polygon_value in value.items():
                    polygon_points = list()
                    if len(polygon_value.get('polygon_vertex_list')) == 1:
                        for polygon_point in polygon_value.get('polygon_vertex_list')[0].get('polygon_vertex'):
                            point = list()
                            point.append(polygon_point.get('x'))
                            point.append(polygon_point.get('y'))
                            polygon_points.append(point)
                    else:
                        print("车牌关键点元素个数不对")
                        print(polygon_value.get('polygon_vertex_list'))
                        exit()
                    shape = {"label": "polygon", "points": polygon_points, "group_id": None, "shape_type": "polygon", "flags": {}, 'text': None}
                    labelme_data.get('shapes').append(shape)
        return labelme_data
