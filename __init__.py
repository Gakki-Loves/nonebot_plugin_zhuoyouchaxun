#'''
#Author: Gakkilove 739150373@qq.com
#Date: 2023-01-14 11:02:34
#LastEditors: Gakkilove 739150373@qq.com
#LastEditTime: 2023-01-14 11:09:51
#FilePath: \nonebot_plugin_zhuoyouchaxun\get_data.py
#Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
#'''

from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

import asyncio
from nonebot import on_command
from nonebot import on_notice
from nonebot.plugin import on_keyword,on_regex
from nonebot.adapters.onebot.v11 import Bot, Event,NoticeEvent
from nonebot.adapters.onebot.v11.message import Message
import nonebot
from nonebot.adapters.onebot.v11 import (GROUP, PRIVATE_FRIEND, Bot,
                                         GroupMessageEvent, Message,
                                         MessageEvent, MessageSegment,
                                         PrivateMessageEvent,GroupIncreaseNoticeEvent)
import sqlite3
from pathlib import Path
import os
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.exception import ActionFailed

from nonebot import on_request
from  nonebot . params  import  Arg ,  CommandArg ,  ArgPlainText 
from .get_data import get_idname,get_BGinfo,get_tubaoname,get_tubaoinfo,runcar,searchcar



# ──────▄▀▄─────▄▀▄
# ─────▄█░░▀▀▀▀▀░░█▄
# ─▄▄──█░░░░░░░░░░░█──▄▄
# █▄▄█─█░░▀░░┬░░▀░░█─█▄▄█
                            
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


# --------------- 复用的功能 ---------------




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
            #如果查询到，则ifchaxun为真，需要got接收参数
            state['ifchaxun'] = True
        # 如果为false，说明没有这个信息
        else:
            message = idname[1]+idname[2]
            message_list.append(message)
            #如果没查询到，则ifchaxun为假，got直接finish
            state['ifchaxun'] = False

    # 为后面撤回消息做准备
    zhuoyou_msg_id = []


    # 尝试发送
    try:
        if state['ifchaxun'] == True:
            if isinstance(event, PrivateMessageEvent):
                for msg in message_list:
                    #await chaxun.send(msg)
                    zhuoyou_msg_id.append((await chaxun.send(msg))['message_id'])
                    await asyncio.sleep(0.5)
            elif isinstance(event, GroupMessageEvent):
                msgs = []
                for msg in message_list:
                    msgs.append({
                    'type': 'node',
                    'data': {
                        'name': "梨花酱",
                        'uin': bot.self_id,
                        'content': msg
                    }
                    })
                zhuoyou_msg_id.append((await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs))['message_id'])
        elif state['ifchaxun'] == False:
            for msg in message_list:
                    #await chaxun.send(msg)
                    zhuoyou_msg_id.append((await chaxun.send(msg))['message_id'])
                    await asyncio.sleep(0.5)
    #若发送失败
    except ActionFailed as F:
        logger.warning(F)
        await chaxun.finish(
            message=Message(f"信息太多梨花记不住啦！让我缓缓~"),
            at_sender=True
        )
    

    # 收到用户需要查询的桌游ID
    #桌游ID只能是3-4位：^\d{3,4}$
@chaxun.got("BGid")
async def _(bot:Bot,event:MessageEvent,state: T_State,BGID: str = ArgPlainText("BGid")):
    #判定是否查询到，没查询到就不需要got接收参数了
    if state['ifchaxun'] == True:
        pass
        bg_data = get_BGinfo(BGID)

        message_list = []
        for idname in bg_data:
        # 如果idname0的状态为True，说明有这个信息,并且通过群聊转发发送
            if idname[0]:               
                message = Message(idname[1])
                message_list.append(message)
                if isinstance(event,PrivateMessageEvent):
                    for msg in message_list:
                        #await chaxun.send(msg)
                        await chaxun.send(msg)
                        #await 
                        await asyncio.sleep(0.5)
                elif isinstance(event,GroupMessageEvent):
                    msgs = []
                    for msg in message_list:
                        msgs.append({
                        'type': 'node',
                        'data': {
                        'name': "梨花酱",
                        'uin': bot.self_id,
                        'content': msg
                        }
                        })
                    await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
        # 如果为false，说明没有这个信息，直接发送
            else:
                message = idname[1]+idname[2]
                message_list.append(message)
                for msg in message_list:
                        #await chaxun.send(msg)
                        await chaxun.send(msg)
                        #await 
                        await asyncio.sleep(0.5)
    else:
        await chaxun.finish()
        
    

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
            state['iftubao'] = True
        # 如果为false，说明没有这个信息
        else:
            message = tubao_idname[1]+tubao_idname[2]
            message_list.append(message)
            state['iftubao'] = False

    # 为后面撤回消息做准备
    tubao_msg_id = []


    # 尝试发送
    try:
        if isinstance(event, PrivateMessageEvent):
            for msg in message_list:
                #await chaxun.send(msg)
                tubao_msg_id.append((await tubao.send(msg))['message_id'])
                await asyncio.sleep(0.5)
        elif isinstance(event, GroupMessageEvent):
            msgs = []
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': "梨花酱",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
        await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
    #若发送失败
    except ActionFailed as F:
        logger.warning(F)
        await tubao.finish(
            message=Message(f"不听不听，哄我两句再试试！"),
            at_sender=True
        )

@tubao.got("tubao_id")
async def _(bot:Bot,event:MessageEvent,state: T_State,tubao_id: str = ArgPlainText("tubao_id")):
    #判定是否查询到，没查询到就不需要got接收参数了
    if state['iftubao'] == True:
        tubao_data = get_tubaoinfo(tubao_id)

        message_list = []
        for tubao_link in tubao_data:
            # 如果idname0的状态为True，说明有这个信息
            if tubao_link[0]:               
                message = Message(tubao_link[1])
                message_list.append(message)
            # 如果为false，说明没有这个信息
            else:
                message = tubao_link[1]+tubao_link[2]
                message_list.append(message)
        if isinstance(event, PrivateMessageEvent):
            for msg in message_list:
                #await chaxun.send(msg)
                await tubao.send(msg)
                await asyncio.sleep(0.5)
        elif isinstance(event, GroupMessageEvent):
            msgs = []
            for msg in message_list:
                msgs.append({
                    'type': 'node',
                    'data': {
                        'name': "梨花酱",
                        'uin': bot.self_id,
                        'content': msg
                    }
                })
            await bot.call_api('send_group_forward_msg', group_id=event.group_id, messages=msgs)
    else:
        await tubao.finish()



# ----------------------发车------------------------------
run_car = on_command("桌游发车",block=True,priority=10)
@run_car.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    # 用state字典把这里获取的user_id保存
    state['userid'] = str(event.user_id)
    await run_car.send("请输入发车信息")

@run_car.got("content")
async def _(state:T_State,content: str = ArgPlainText("content"),prompt="模板"):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['content'] = content
    await run_car.send("请输入截止时间~例如“21:50”")
    #runcar(car_id,content)

@run_car.got("deadline")
async def _(state:T_State,deadline: str = ArgPlainText("deadline")):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['deadline'] = deadline
    deadline = deadline.replace("：", ":")
    if "24:00">=deadline>="00:00":
        car_id = str(state['userid'])
        content = str(state['content'])
        runcar(car_id,content,deadline)
    else:
        await run_car.finish("敲你脑袋哦！时间要正确填写！")
    #runcar(car_id,content)
### -发完车的广播功能未写

# -----------------------查车-----------------------
search_car = on_command("桌游查车",block=True,priority=11)
@search_car.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    # 用state字典把这里获取的user_id保存
    #state['userid'] = str(event.user_id)
    msg = searchcar()
    ### -查车返回功能没写
# -----------------------------------------------------

# -----------------------cheche表每天删除-----------------------
# 定时任务函数
def clear_table():
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    c = conn.cursor()
    c.execute(f'DELETE FROM cheche')
    conn.commit()
    print('Clear table successfully!')


# 将函数注册为定时任务
@scheduler.scheduled_job('cron', hour='0')
async def _():
    clear_table()

# -----------------------------------------------------



# -----------------------帮助菜单-----------------------
#
# -----------------------------------------------------


# ------------------欢迎新群友----------------
# -初始化
notice_handle  = on_notice ( priority =5,  block =True ) 

@notice_handle.handle () 
async  def  GroupNewMember ( bot :  Bot ,  event :  GroupIncreaseNoticeEvent ): 
    if  event . user_id  == event . self_id : 
        await  bot . send_group_msg ( group_id =event . group_id ,  message =Message ( 
            MessageSegment . text ( '小伙伴们好呀~我是梨花酱，是桌游图书馆的管理员哦~\n' ) ) )
    else:
        await bot.send_group_msg ( group_id =event . group_id ,  message =Message ( 
            MessageSegment . at ( event . user_id )  + MessageSegment . text ( "欢迎新桌友哦~我是桌游图书馆管理员梨花酱，请注意查看群公告内容~\n" ))) 