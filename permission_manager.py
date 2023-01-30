#'''
#Author: Gakkilove 739150373@qq.com
#Date: 2023-01-30 21:57:25
#LastEditors: Gakkilove 739150373@qq.com
#LastEditTime: 2023-01-30 21:59:16
#FilePath: \nonebot_plugin_zhuoyouchaxun\permission_manager.py
#Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
#'''
import os
import random
import time
from pathlib import Path
from ast import literal_eval

import nonebot
from nonebot.log import logger


try:
    import ujson as json
except:
    logger.warning('ujson not find, import json instead')
    import json

#{
    #全局变量：
    #broadcast_runner ：多群轮播开车信息
#}'''

class PermissionManager:
    def __init__(self) -> None:
        # 读取全局变量
        try: 
            self.LihuaBot_cfg_path  = str(Path(nonebot.get_driver().config.LihuaBot_cfg_path,'LihuaBot_cfg.json'))
        except:
            self.LihuaBot_cfg_path  = 'data/LihuaBot/LihuaBot_cfg.json'
        try: 
            self.broadcast_runner             = int(nonebot.get_driver().config.broadcast_runner)
        except:
            self.broadcast_runner             = False

        #读取cfg文件
        self.ReadCfg()

    # --------------- 文件读写 开始 ---------------
    # 读取cfg
    def ReadCfg(self)->dict:
        try:
            # 尝试读取
            with open(self.LihuaBot_cfg,'r',encoding='utf-8') as f:
                self.cfg = json.loads(f.read())
            return self.cfg
        except Exception as e:
            # 读取失败
            logger.warning(f'LihuaBot_cfg.json 读取失败, 尝试重建\n{e}')
            self.cfg = {}
            self.WriteCfg()
            return {}
    
    # 写入cfg
    def WriteCfg(self):
        # 尝试创建路径
        os.makedirs(self.LihuaBot_cfg_path[:-18],mode=0o777,exist_ok=True)
        # 写入数据
        with open(self.LihuaBot_cfg_path,'w',encoding='utf-8') as f:
            f.write(json.dumps(self.cfg))
    # --------------- 文件读写 ---------------

    #---------------- 查询部分 -------------------
    def search_broadcast_runcar(self):
        return self.cfg['broadcast_runcar']


    #-----------------逻辑部分--------------------


    # 多群轮播功能
    def broadcast_runcar(self,broadcast_runcar):
        # 读取原有数据
        # try:
            # switch = self.cfg['broadcast_runcar']
        # except KeyError:
            # switch = '未设定'
        #写进全局变量
        self.cfg['broadcast_runcar'] = broadcast_runcar
        self.WriteCfg()
