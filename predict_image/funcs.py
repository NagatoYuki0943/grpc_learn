import numpy as np
import cv2
import base64
import time
import os
import json
import object_detect_pb2
import xml.etree.ElementTree as ET
from xml.etree.ElementTree import fromstring
import copy


SERVER_SAVE_PATH = "server"
os.makedirs(SERVER_SAVE_PATH, exist_ok=True)
SAVE = True # 是否保存图片和xml


def detect(request: object_detect_pb2.Request) -> tuple[bytes, str]:
    """检测
    """
    #=====================接收图片=====================#
    # 解码图片                               image是Request中设定的变量
    image_decode = base64.b64decode(request.image)
    # 变成一个矩阵 单维向量
    array = np.frombuffer(image_decode, dtype=np.uint8)
    # print("array shape:", array.shape)
    # 再解码成图片 三维图片
    image_bgr = cv2.imdecode(array, cv2.IMREAD_COLOR)
    print("image shape:", image_bgr.shape)

    #=====================修改图片=====================#
    cross = np.random.uniform(0, 1, image_bgr.shape)
    image = image_bgr * cross
    image = image.astype(np.uint8)

    #=====================编码图片=====================#
    # 返回True和编码,这里只要编码
    image_encode = cv2.imencode(".jpg", image)[1]
    # image_bytes = image_encode.tobytes()
    # image_64 = base64.b64encode(image_bytes)
    image_64 = base64.b64encode(image_encode)

    #=====================编码结果=====================#
    # 假设检测结果
    detect = {
        "detect": [
            {
                "class_index": 0,
                "class": "person",
                "confidence": 0.8797998428344727,
                "box": [
                    670,
                    390,
                    810,
                    880
                ]
            },
            {
                "class_index": 5,
                "class": "bus",
                "confidence": 0.8578267097473145,
                "box": [
                    15,
                    221,
                    801,
                    791
                ]
            },
            {
                "class_index": 0,
                "class": "person",
                "confidence": 0.6044366955757141,
                "box": [
                    0,
                    552,
                    68,
                    875
                ]
            }
        ],
        "num": {
            0: 2,
            5: 1
        },
        "image_size": [
            1080,
            810,
            3
        ]
    }

    #================保存图片和检测结果=================#
    if SAVE:
        file_name = str(time.time())
        cv2.imwrite(os.path.join(SERVER_SAVE_PATH, file_name + ".jpg"), image_bgr)
        json2xml(detect, file_name)

    detect_str = json.dumps(detect)

    return image_64, detect_str


def indent(elem, level=0):
    """缩进xml
    https://www.cnblogs.com/muffled/p/3462157.html
    """
    i = "\n" + level*"\t"
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "\t"
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
        for elem in elem:
            indent(elem, level+1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i


xml_string = """
<annotation>
	<folder>VOC2007</folder>
	<filename>000001.jpg</filename>
	<source>
		<database>The VOC2007 Database</database>
		<annotation>PASCAL VOC2007</annotation>
		<image>flickr</image>
		<flickrid>341012865</flickrid>
	</source>
	<owner>
		<flickrid>Fried Camels</flickrid>
		<name>Jinky the Fruit Bat</name>
	</owner>
	<size>
		<width>353</width>
		<height>500</height>
		<depth>3</depth>
	</size>
	<segmented>0</segmented>
	<object>
		<name>dog</name>
		<pose>Left</pose>
		<truncated>1</truncated>
		<difficult>0</difficult>
		<bndbox>
			<xmin>48</xmin>
			<ymin>240</ymin>
			<xmax>195</xmax>
			<ymax>371</ymax>
		</bndbox>
	</object>
</annotation>
"""
root = fromstring(xml_string)
# 获取临时object
base_object = copy.deepcopy(root.find("object"))


def json2xml(data: dict, file_name: str):
    """将检测的json转换为xml并保存

    Args:
        data (dict):      json数据
        file_name (str):  文件名
    """
    # 删除全部的object
    for o in root.findall("object"):
        root.remove(o)

    # 保存文件名
    root.find("filename").text = file_name + ".jpg"

    # 保存图片大小通道
    root.find("size").find('height').text = str(data["image_size"][0])
    root.find("size").find('width').text  = str(data["image_size"][1])
    root.find("size").find('depth').text  = str(data["image_size"][2])

    # 循环遍历保存框
    rectangles = data["detect"]
    for rectange in rectangles:
        # 需要重新copy,不然多个框只会保存最后一个
        temp_object = copy.deepcopy(base_object)
        # 保存类别名称和坐标
        temp_object.find("name").text = rectange["class"]

        temp_object.find("bndbox").find("xmin").text = str(rectange["box"][0])
        temp_object.find("bndbox").find("ymin").text = str(rectange["box"][1])
        temp_object.find("bndbox").find("xmax").text = str(rectange["box"][2])
        temp_object.find("bndbox").find("ymax").text = str(rectange["box"][3])

        # 将框保存起来
        root.append(temp_object)

    # 缩进root
    indent(root)
    new_tree = ET.ElementTree(root)
    xml_path = os.path.join(SERVER_SAVE_PATH, file_name+".xml")
    # 打开使用utf-8,写入时也需要utf-8
    new_tree.write(xml_path, encoding="utf-8")
