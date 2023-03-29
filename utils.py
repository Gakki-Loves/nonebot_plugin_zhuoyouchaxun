from pathlib import Path
from nonebot.log import logger

import os
import random

try:
    import ujson as json
except ModuleNotFoundError:
    import json

path = os.path.join(os.path.dirname(__file__), ("resource"/"group_words"))

# 载入个人词库
lst = os.listdir(Path(path))


MyThesaurus = {}
for i in lst:
    try:
        tmp = json.load(open(Path(path) / i, "r", encoding="utf8"))
        logger.info(f"{i} 加载成功~")
        for key in tmp.keys():
            if not key in MyThesaurus.keys():
                MyThesaurus.update({key:[]})
            if type(tmp[key]) == list:
                MyThesaurus[key] += tmp[key]
            else:
                logger.info(f"\t文件 {i} 内 {key} 词条格式错误。")
    except UnicodeDecodeError:
        logger.info(f"{i} utf8解码出错！！！")
    except Exception as error:
        logger.info(f"错误：{error} {i} 加载失败...")

# 载入词库
normalwords = json.load(open(Path(path) / "normalwords.json", "r", encoding="utf8"))




# 向bot打招呼
hello__bot = [
    "你好啊",
    "你好",
    "在吗",
    "在不在",
    "您好",
    "您好啊",
    "你好",
    "在",
    "早",
]


# hello之类的回复
hello__reply = [
    "你好呀~我是梨花，请问有什么可以帮到您？",
    "诶嘿..？！",
    "你好OvO",
    "唔唔 ~ ，叫梨花做什么呢☆",
    "怎么了啦qwq",
    "梨花才没有走神呢",
    "halo ~ 叫可爱的梨花有什么事嘛OvO",
    "你好~欢迎来到桌游图书馆~我是全世界最可爱的梨花！"
]





def get_chat_result(resource:dict, text: str) -> str:
    """
    从 resource 中获取回应
    """
    if len(text) < 21:
        keys = resource.keys()
        for key in keys:
            if text.find(key) != -1:
                return random.choice(resource[key])

