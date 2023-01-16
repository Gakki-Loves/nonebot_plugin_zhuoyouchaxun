#'''
#Author: Gakkilove 739150373@qq.com
#Date: 2023-01-14 11:02:34
#LastEditors: Gakkilove 739150373@qq.com
#LastEditTime: 2023-01-14 11:09:51
#FilePath: \nonebot_plugin_zhuoyouchaxun\get_data.py
#Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
#'''

import asyncio
from nonebot.plugin import on_keyword,on_regex
from nonebot.adapters.onebot.v11 import Bot, Event
from nonebot.adapters.onebot.v11.message import Message
import nonebot
from nonebot.adapters.onebot.v11 import (GROUP, PRIVATE_FRIEND, Bot,
                                         GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PrivateMessageEvent)

from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.exception import ActionFailed

from  nonebot . params  import  Arg ,  CommandArg ,  ArgPlainText 
from .get_data import get_idname,get_BGinfo,get_tubaoname

#hello = on_keyword(['桌游查询','今日人品'],priority=50)
#@hello.handle()
#async def hello_handle(bot: Bot, event: Event):
    #await bot.send(
        #event=event,
        #message="Hello"
    #)

# -------------- 初始化变量 -------------------
# 读取桌游信息查询的正则表达
try:
    chaxun_regex = repr(nonebot.get_driver().config.chaxun_regex)
except:
    chaxun_regex = r"^(桌游查询|zycx)\s?([\u4E00-\u9FA5A-Za-z0-9]+$)"  #桌游查询 卡坦岛

# 读取图包信息查询的正则表达
try:
    chaxun_tubao = repr(nonebot.get_driver().config.chaxun_tubao)
except:
    chaxun_tubao = r"^(图包查询|tbcx)\s?([\u4E00-\u9FA5A-Za-z0-9]+$)"  #桌游查询 卡坦岛




# --------------发送查询信息部分-----------------
# 桌游查询的正则表达式
chaxun = on_regex(
    chaxun_regex,
    priority=20,
    block=True
)

#响应器处理
@chaxun.handle()
async def _(bot: Bot, event: MessageEvent,state: T_State):
    args = list(state["_matched_groups"])
    name = args[1]  #读取桌游名称

    #此时应该从用name查询数据库，返回所有包含name的桌游id和桌游name
    data_idname =  get_idname(name)        #data应该返回id和name


    # 消息发送列表
    message_list = []
    for idname in data_idname:
        # 如果idname0的状态为True，说明有这个信息
        if idname[0]:               
            message = f"请输入你要查询的桌游ID：\n"+Message(idname[1])
            message_list.append(message)
        # 如果为false，说明没有这个信息
        else:
            message = idname[1]+idname[2]
            message_list.append(message)

    # 为后面撤回消息做准备
    zhuoyou_msg_id = []


    # 尝试发送
    try:
        for msg in message_list:
            #await chaxun.send(msg)
            zhuoyou_msg_id.append((await chaxun.send(msg))['message_id'])
            await asyncio.sleep(0.5)
    #若发送失败
    except ActionFailed as F:
        logger.warning(F)
        await chaxun.finish(
            message=Message(f"梨花酱被风控了呢！请联系主人将我解封哦~"),
            at_sender=True
        )
    

    # 收到用户需要查询的桌游ID
    #桌游ID只能是3-4位：^\d{3,4}$
@chaxun.got("BGid")
async def _(BGID: str = ArgPlainText("BGid")):
    #BGID
    bg_data = get_BGinfo(BGID)

    message_list = []
    for idname in bg_data:
        # 如果idname0的状态为True，说明有这个信息
        if idname[0]:               
            message = Message(idname[1])
            message_list.append(message)
        # 如果为false，说明没有这个信息
        else:
            message = idname[1]+idname[2]
            message_list.append(message)

    for msg in message_list:
            #await chaxun.send(msg)
            await chaxun.send(msg)
            await asyncio.sleep(0.5)

# 图包查询的正则表达式
tubao = on_regex(
    chaxun_tubao,
    priority=20,
    block=True
)
@tubao.handle()
async def _(bot: Bot, event: MessageEvent,state: T_State):
    args = list(state["_matched_groups"])
    tubao_name = args[1]  #读取桌游名称

    #此时应该从用tubao_name查询数据库，返回所有包含tubao_name的图包id和图包name
    tubao_idname =  get_tubaoname(tubao_name)        #data应该返回id和name


    # 消息发送列表
    message_list = []
    for tubao_idname in tubao_idname:
        # 如果idname0的状态为True，说明有这个信息
        if tubao_idname[0]:               
            message = f"请输入你要查询的图包ID：\n"+Message(tubao_idname[1])
            message_list.append(message)
        # 如果为false，说明没有这个信息
        else:
            message = tubao_idname[1]+tubao_idname[2]
            message_list.append(message)

    # 为后面撤回消息做准备
    tubao_msg_id = []


    # 尝试发送
    try:
        for msg in message_list:
            #await chaxun.send(msg)
            tubao_msg_id.append((await tubao.send(msg))['message_id'])
            await asyncio.sleep(0.5)
    #若发送失败
    except ActionFailed as F:
        logger.warning(F)
        await tubao.finish(
            message=Message(f"梨花酱被风控了呢！请联系主人将我解封哦~"),
            at_sender=True
        )
    