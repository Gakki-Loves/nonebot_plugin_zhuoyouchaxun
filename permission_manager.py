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
import configparser

try:
    import ujson as json
except:
    logger.warning('ujson not find, import json instead')
    import json




'''{
    'broadcast_runcar'     :False,      #多群广播总功能
    'group_114541':{
        # 桌游相关功能
        'search_boardgame' : True,     # 桌游查询
        'search_mod'       : True,     # 图包查询
        'run_car'          : True,     # 桌游发车
        'search_car'       : True,     # 桌游查车
        'broadcastruncar' : True,      # 是否发送多群广播车主信息
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
            self.search_boardgame             = True
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
        try:    
            self.broadcastruncar             = int(nonebot.get_driver().config.broadcast_runcar)
        except:
            self.broadcastruncar             = True

        #读取cfg文件
        self.ReadCfg()

    # --------------- 文件读写 开始 ---------------
    # 读取cfg
    def ReadCfg(self:str)->dict:
        try:
            # 尝试读取
            with open(self.LihuaBot_cfg_path,'r',encoding='utf-8') as f:
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
    # 查询 多群广播总开关
    def Query_broadcast_runcar(self):
        try:
            # 有设置就返回设置的
            return self.cfg['broadcast_runcar']
        except KeyError:
            # 没设置就返回默认的全局变量
            return self.broadcast_runner

    # 查询 “桌游查询”功能
    def Query_search_boardgame(self,sessionId:str):
        try:
            # 有设置就返回设置的
            return self.cfg[sessionId]['search_boardgame']
        except KeyError:
            # 没设置就返回默认的全局变量
            return self.search_boardgame

    # 查询 “图包查询”功能
    def Query_search_mod(self,sessionId:str):
        try:
            # 有设置就返回设置的
            return self.cfg[sessionId]['search_mod']
        except KeyError:
            # 没设置就返回默认的全局变量
            return self.search_mod

    # 查询 “桌游发车”功能
    def Query_run_car(self,sessionId:str):
        try:
            # 有设置就返回设置的
            return self.cfg[sessionId]['run_car']
        except KeyError:
            # 没设置就返回默认的全局变量
            return self.run_car

    # 查询 “桌游查车”功能
    def Query_search_car(self,sessionId:str):
        try:
            # 有设置就返回设置的
            return self.cfg[sessionId]['search_car']
        except KeyError:
            # 没设置就返回默认的全局变量
            return self.search_car

    # 查询 “多群广播”功能
    def Query_broadcastruncar(self,sessionId:str):
        try:
            # 有设置就返回设置的
            return self.cfg[sessionId]['broadcastruncar']
        except KeyError:
            # 没设置就返回默认的全局变量
            return self.broadcastruncar
    #-----------------逻辑部分--------------------


    
    #-----------------增减部分--------------------
    #白名单部分，用于创建群的权限列表
    def UpdateWhiteList(self,sessionId:str,add_mode:bool):
        # 白名单部分
        if add_mode:
            if sessionId in self.cfg.keys():
                return f'{sessionId}已在白名单'
            self.cfg[sessionId] = {}
            self.WriteCfg()
            return f'成功添加{sessionId}至白名单'
        # 移除出白名单
        else:
            if sessionId in self.cfg.keys():
                self.cfg.pop(sessionId)
                self.WriteCfg()
                return f'成功移除{sessionId}出白名单'
            return f'{sessionId}不在白名单'
    
    # 多群广播功能
    def broadcast_runcar(self,broadcast_runcar:bool):
        self.cfg['broadcast_runcar'] = broadcast_runcar
        self.WriteCfg()

    # 桌游查询部分
    def Update_search_boardgame(self,sessionId:str,search_boardgame:bool):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 读取原有数据
        if search_boardgame:
            self.cfg[sessionId]['search_boardgame'] = True
            self.WriteCfg()
            return f'成功开启{sessionId}的桌游查询权限'
        else:
            self.cfg[sessionId]['search_boardgame'] = False
            self.WriteCfg()
            return f'成功关闭{sessionId}的桌游查询权限'


    # 图包查询部分
    def Update_search_mod(self,sessionId:str,search_mod:bool):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        if search_mod:
            self.cfg[sessionId]['search_mod'] = True
            self.WriteCfg()
            return f'成功开启{sessionId}的图包查询权限'
        else:
            self.cfg[sessionId]['search_mod'] = False
            self.WriteCfg()
            return f'成功关闭{sessionId}的图包查询权限'

    # 桌游发车部分
    def Update_run_car(self,sessionId:str,run_car:bool):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        if run_car:
            self.cfg[sessionId]['run_car'] = True
            self.WriteCfg()
            return f'成功开启{sessionId}的桌游发车权限'
        else:
            self.cfg[sessionId]['run_car'] = False
            self.WriteCfg()
            return f'成功关闭{sessionId}的桌游发车权限'
    # 桌游查车部分
    def Update_search_car(self,sessionId:str,search_car:bool):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        if search_car:
            self.cfg[sessionId]['search_car'] = True
            self.WriteCfg()
            return f'成功开启{sessionId}的桌游查车权限'
        else:
            self.cfg[sessionId]['search_car'] = False
            self.WriteCfg()
            return f'成功关闭{sessionId}的桌游查车权限'
    # 是否发送多群广播车主信息
    def Update_broadcastruncar(self,sessionId:str,broadcastruncar:bool):
        # 检查是否已在白名单, 不在则结束
        if not sessionId in self.cfg.keys():
            return f'{sessionId}不在白名单, 请先添加至白名单后操作'
        # 检查数据是否超出范围，超出则设定至范围内
        # 读取原有数据
        if broadcastruncar:
            self.cfg[sessionId]['broadcastruncar'] = True
            self.WriteCfg()
            return f'成功开启群号为{sessionId}的多群广播接收权限，该群不会收到多群广播的信息了'
        else:
            self.cfg[sessionId]['broadcastruncar'] = False
            self.WriteCfg()
            return f'成功关闭群号为{sessionId}的多群广播接收权限，该群不会收到多群广播的信息了'
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

