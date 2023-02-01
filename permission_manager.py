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



'''{
    'broadcast_runcar'     :False,      #多群轮播
    'group_114541':{
        # 桌游相关功能
        'search_boardgame' : True,     # 桌游查询
        'search_mod'       : True,     # 图包查询
        'run_car'          : True,     # 桌游发车
        'search_car'       : True,     # 桌游查车
    },
    'last':{
        'user_1919' : 810    # 最近一次发送时间
    },
    'ban':[
        'user_1919',         # 禁用的群组或用户，跨会话生效，会覆盖白名单设置
        'group_810'
    ]
}'''

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
        try: 
            self.search_boardgame             = int(nonebot.get_driver().config.search_boardgame)
        except:
            self.broadcast_runner             = True
        try: 
            self.search_mod                   = int(nonebot.get_driver().config.search_mode)
        except:
            self.search_mod                   = True
        try:    
            self.run_car                      = int(nonebot.get_driver().config.run_car)
        except:
            self.run_car                      = True
        try:    
            self.search_car                   = int(nonebot.get_driver().config.search_car)
        except:
            self.search_car                   = True

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


    
    #-----------------增减部分--------------------

    # 多群轮播功能
    def broadcast_runcar(self,broadcast_runcar:bool):
        self.cfg['broadcast_runcar'] = broadcast_runcar
        self.WriteCfg()

    # 桌游查询部分
    def Update_search_boardgame(self,sessionId:str,search_boardgame:bool):
        # 检查是否已在白名单, 不在则结束
        # if not sessionId in self.cfg.keys():
            #return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        try:
            search_boardgame_old = self.cfg[sessionId]['search_boardgame']
        except KeyError:
            search_boardgame_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['cd'] = search_boardgame
        self.WriteCfg()
        # 返回信息
        return f'成功更改桌游查询功能 {search_boardgame_old} -> {search_boardgame}'

    # 图包查询部分
    def Update_search_mod(self,sessionId:str,search_mod:bool):
        # 检查是否已在白名单, 不在则结束
        # if not sessionId in self.cfg.keys():
            #return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        try:
            search_mod_old = self.cfg[sessionId]['search_mod']
        except KeyError:
            search_mod_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['cd'] = search_mod
        self.WriteCfg()
        # 返回信息
        return f'成功更改图包查询功能 {search_mod_old} -> {search_mod}'

    # 桌游发车部分
    def Update_run_car(self,sessionId:str,run_car:bool):
        # 检查是否已在白名单, 不在则结束
        # if not sessionId in self.cfg.keys():
            #return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        try:
            run_car_old = self.cfg[sessionId]['run_car']
        except KeyError:
            run_car_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['cd'] = run_car
        self.WriteCfg()
        # 返回信息
        return f'成功更改桌游发车功能 {run_car_old} -> {run_car}'

    # 桌游查车部分
    def Update_search_car(self,sessionId:str,search_car:bool):
        # 检查是否已在白名单, 不在则结束
        # if not sessionId in self.cfg.keys():
            #return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        try:
            search_car_old = self.cfg[sessionId]['run_car']
        except KeyError:
            search_car_old = '未设定'
        # 写入新数据
        self.cfg[sessionId]['cd'] = search_car
        self.WriteCfg()
        # 返回信息
        return f'成功更改桌游查车功能 {search_car_old} -> {search_car}'

    # 黑名单部分
    # add_mode = True，加入黑名单；add_mode = False，移除黑名单
    def UpdateBanList(self,sessionId:str,add_mode:bool):
        # 加入黑名单
        if add_mode:
            try:
                if sessionId in self.cfg['ban']:
                    return f'{sessionId}已在黑名单'
            except KeyError:
                self.cfg['ban'] = []
            self.cfg['ban'].append(sessionId)
            self.WriteCfg()
            return f'成功添加{sessionId}至黑名单'
        # 移出黑名单
        else:
            try:
                self.cfg['ban'].remove(sessionId)
                self.WriteCfg()
                return f'成功移除{sessionId}出黑名单'
            except ValueError:
                return f'{sessionId}不在黑名单'



#------------------------------权限控制相关函数-----------------------------------

