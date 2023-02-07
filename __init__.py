
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
from nonebot import on_command,on_notice,on_request

from nonebot.plugin import on_keyword,on_regex
from nonebot.adapters.onebot.v11 import Bot, Event,NoticeEvent
from nonebot.adapters.onebot.v11.message import Message
import nonebot
from nonebot.adapters.onebot.v11 import (GROUP, PRIVATE_FRIEND, Bot,
                                         GroupMessageEvent, Message,
                                         MessageEvent,MessageSegment,
                                         PrivateMessageEvent,GroupIncreaseNoticeEvent,
                                         GroupRequestEvent,RequestEvent)
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER
import sqlite3
from pathlib import Path
import os
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from .permission_manager import PermissionManager

from  nonebot . params  import  Arg ,  CommandArg ,  ArgPlainText 
from .get_data import get_idname,get_BGinfo,get_tubaoname,get_tubaoinfo,runcar,searchcar
import time # 快乐小隆要用做时间转换
import re # 快乐小隆要用做时间转换

#======================================================================================
#===================================快乐小隆功能区=========================================
#======================================================================================


# ──────▄▀▄─────▄▀▄
# ─────▄█░░▀▀▀▀▀░░█▄
# ─▄▄──█░░░░░░░░░░░█──▄▄
# █▄▄█─█░░▀░░┬░░▀░░█─█▄▄█
                            
# -------------- 初始化变量 -------------------
# 实例化权限管理
pm = PermissionManager()
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
# 根据会话类型生成sessionId
def sessionId(event:MessageEvent):
    if isinstance(event, PrivateMessageEvent):
        sessionId = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        sessionId = 'group_' + str(event.group_id)
    return sessionId

# 分析sdssionId是否正确
def verifySid(sid:str):
    try:
        sType, sId = sid.split('_')
        if sType in ['group','user']:
            if sId.isdigit():
                return True
        return False
    except:
        return False


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

    # 功能开启判定
    if isinstance(event, PrivateMessageEvent):
        state['sid'] = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        state['sid'] = 'group_' + str(event.group_id)
    cmd_search_boardgame = pm.Query_search_boardgame(state['sid'])
    if cmd_search_boardgame == False:
        await chaxun.finish("桌游查询功能没有开启哦~")

    # ---逻辑部分
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
            #如果没查询到，则ifchaxun为假直接finish
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
                    zhuoyou_msg_id.append((await chaxun.finish(msg))['message_id'])
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

    # 功能开启判定
    if isinstance(event, PrivateMessageEvent):
        state['sid'] = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        state['sid'] = 'group_' + str(event.group_id)
    cmd_search_boardgame = pm.Query_search_mod(state['sid'])
    if cmd_search_boardgame == False:
        await chaxun.finish("图包查询功能没有开启哦~")

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
        if state['iftubao'] == True:
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
        elif state['iftubao'] == False:
            for msg in message_list:
                    #await chaxun.send(msg)
                    await tubao.finish(msg)
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
run_car = on_command("桌游发车",block=True,priority=10,aliases={"发车"})

@run_car.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):

    # 功能开启判定
    if isinstance(event, PrivateMessageEvent):
        state['sid'] = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        state['sid'] = 'group_' + str(event.group_id)
    cmd_search_boardgame = pm.Query_run_car(state['sid'])
    if cmd_search_boardgame == False:
        await chaxun.finish("桌游发车功能没有开启哦~")

    # 用state字典把这里获取的user_id保存
    state['userid'] = str(event.user_id)
    await run_car.send("请输入发车信息，例如：\n《桌游名》\n【人数】X=X\n【教学】带教学\n【类型】美式/战斗\n【时长】教15分钟；玩60分钟\n【扩展】不带扩\n【难度】bgg(2.03 / 5)；集石(4/10)\n【房名】XXX\n【密码】XXX\n【语音】https://kook.top/XXX\nPS： 这是一辆车车的模板")

@run_car.got("content")
async def _(state:T_State,content: str = ArgPlainText("content"),prompt="模板"):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['content'] = content
    await run_car.send("请输入截止时间~例如“21:50”")


@run_car.got("deadline")
async def _(bot: Bot,state:T_State,event: GroupMessageEvent,deadline: str = ArgPlainText("deadline")):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['deadline'] = deadline
    deadline = deadline.replace("：", ":")
    matchObj = re.match(r"^([0-9]|1[0-9]|2[0-3]|0[0-9]):([0-9]|[1-5]\d|0[0-9])$", deadline, re.I)#正则表达式，来检验AA:BB这样的时间，其中AA的范围是0-23和00-23，BB的范围是00-59和0-59
    if(matchObj!=None):# 如果上面这个re.match函数匹配到东西了，也就是matchObj的结果不为None那说明用户输入的时间是正确的
        timeArray = time.strptime(deadline, "%H:%M") # 把用户输入的时间拆分为后续把9:31这样的“少0”的时间变成正常的XX:XX格式的时间
        hour=timeArray[3] # 小时
        min=timeArray[4] # 分钟
        if(hour>=0 and hour<=9): #
            deadline='0'+str(hour)+":" # 把0-9点前面加0，这步结束deadline的值应该是变成00，01，02，···，09
        else:
            deadline=str(hour)+":"# 如果小时是11-23那就不管，这步结束deadline的值应该是变成10，11，12，···，23
        if(min>=0 and min<=9): 
            deadline=deadline+'0'+str(min) # 把0-9分前面加0
        if "24:00">=deadline>="00:00":# 虽然根据"^[0-23]{1,2}:[0-59]{1,2}$"这个正则表达式，只要能进到if(matchObj!=None):里的时间，都肯定符合"24:00">=deadline>="00:00"这个要求，但为了不删除Gakki的代码，还是把这句话保留下来了
            car_id = str(state['userid'])
            content = str(state['content'])
            runcar(car_id,content,deadline)
    else:
        await run_car.finish("敲你脑袋哦！时间填错啦！请输入“桌游发车”重新操作哦~")
    # ------多群广播发车信息功能
    cmd_broad_cast = pm.Query_broadcast_runcar()
    #cmd_broadcast = pm.Query_broadcastruncar(state['sid'])
    group_list = await bot.get_group_list()
    # 判断是否为主群
    group_id = str(event.group_id)
    if group_id == "177053575":
        if cmd_broad_cast == True:
            # 这里要判断各个群是否开启了接收多群广播功能
            # 没开的就不发送开车信息
            # 本来应该写个函数的
            # 但是我懒
            # 所以就直接写在循环里了
            # 罪过罪过
            allGroupNum=0 # 共有多少群，即梨花加入的所有群数量之和
            onBroadCastGroupNum=0 # 开启了广播功能的有多少群
            for group in group_list:
                allGroupNum+=1
                group_id=group["group_id"]
                sessionId = 'group_' + str(group_id)
                # 找到这个群的多群广播功能开了没
                cmd_broadcast = pm.Query_broadcastruncar(sessionId)
                if cmd_broadcast:
                    onBroadCastGroupNum+=1
                    await bot.send_group_msg(group_id=group["group_id"], message=(content+"\n截止时间："+deadline))
            await run_car.finish(f"梨花一共加入了{allGroupNum}个群，已经帮您广播转发到了{onBroadCastGroupNum}个群，其余群关闭了接收广播功能~")
        elif cmd_broad_cast == False:
            await run_car.finish("多群广播功能没有开启呦~梨花已经帮你记录到车库啦！")
        else:
            await run_car.finish("多群广播设置不正确哦！")
    else:
        await run_car.finish("梨花已经帮你记录到车库啦！\n(第二轮测试期间，发车信息被多群广播只有在梨花的图书馆（群号：177053575）才可以使用哦！)")



# -----------------------查车-----------------------
search_car = on_command("桌游查车",block=True,priority=11,aliases={"查车"})
@search_car.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):

    # 功能开启判定
    if isinstance(event, PrivateMessageEvent):
        state['sid'] = 'user_' + str(event.user_id)
    if isinstance(event, GroupMessageEvent):
        state['sid'] = 'group_' + str(event.group_id)
    cmd_search_boardgame = pm.Query_search_car(state['sid'])
    if cmd_search_boardgame == False:
        await chaxun.finish("桌游查车功能没有开启哦~")



    # 用state字典把这里获取的user_id保存
    message_searchcar = searchcar()
    # 消息发送列表
    message_list = []
    for car_list in message_searchcar:
        # 如果idname0的状态为True，说明有这个信息
        if car_list[0]:               
            message = f"下面是存在的车车哦~"
            message_list.append(message)
            for onecar in car_list[1]:
                message_list.append(onecar)
        # 如果为false，说明没有这个信息
        else:
            message = car_list[1]+car_list[2]
            message_list.append(message)

    # 尝试发送
    try:
        if isinstance(event, PrivateMessageEvent):
            msg = []
            for msg in message_list:
                #await chaxun.send(msg)
                await search_car.send(msg)
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
        await search_car.finish(
            message=Message(f"不听不听，哄我两句再试试！"),
            at_sender=True
        )


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


# -----------------------帮助菜单-----------------------
# 普通命令
lihuahelp = on_command("梨花命令",block=True, priority=10,aliases={"梨花指令","梨花帮助文档","梨花酱 指令","梨花酱指令","梨花帮助","梨花文档","梨花help"})
@lihuahelp.handle()
async def _():
    help_msg = """梨花的使用命令:
    桌游功能：          
    ‘桌游查询 XXX’       查询XXX桌游信息
    ‘图包查询 XXX’       查询XXX图包信息
    ‘桌游查车’/‘查车’    查询正在进行的桌游车
    ‘桌游发车’/‘发车’    你来开一辆车
    (发送”桌游发车“梨花可以把你的约车信息广播到几十个群哦)

    其他功能：
    ‘XX天气’        查询XX未来几天的天气
    ‘占卜/塔罗牌’   占卜功能
    ‘人生重开’      人生重开模拟器
    ‘疯狂星期四’    随机发送疯狂星期四文案
    ‘.send +内容’   可以直接和bot作者对话，提出意见建议
    """
    await lihuahelp.finish(help_msg)

# 管理员命令
lihua_cmdhelp = on_command("梨花管理员命令",permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER,block=True, priority=10,aliases={"梨花管理员指令","梨花管理员帮助文档","梨花酱 管理员指令","梨花酱管理员指令","梨花管理员帮助","梨花管理员文档","梨花管理员help","梨花help管理员"})
@lihua_cmdhelp.handle()
async def _():
    help_msg = """梨花的管理员命令:
    白名单管理：
    lihua_wl add  添加会话至白名单
    lihua_wl del  移出会话自白名单
    
    黑名单管理：    
    lihua_wl add  添加会话至黑名单
    lihua_wl del  移出会话自黑名单

    桌游功能权限：
    lihua_search_boardgame on/off  开启/关闭桌游查询
    lihua_search_mod on/off        开启/关闭图包查询
    lihua_run_car on/off           开启/关闭桌游发车
    lihua_search_car on/off        开启/关闭桌游查车
    lihua_broadcastruncar on/off   开启/关闭本群的多群广播接收功能
    """
    await lihua_cmdhelp.finish(help_msg)

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
            MessageSegment . at ( event . user_id )  + MessageSegment . text ( "欢迎新桌友哦~我是桌游图书馆管理员梨花酱，请注意查看群公告内容~梨花可以帮你查找图包，向几十个群发送您的约车信息~发送“梨花命令”四个字可以获得梨花的命令目录哦~\n" ))) 



# -----------------------------------------------------------------------------------
# -------------------------------- 权限管理部分 --------------------------------------
# -----------------------------------------------------------------------------------

#------------------------超级用户权限-------------------------
# -----查看群列表（超级用户专用）
search_group_list = on_command("查看群列表",permission=SUPERUSER)
@search_group_list.handle()
async def _(bot: Bot, event: MessageEvent):
    group_list = await bot.get_group_list()
    message = f"梨花已加入的群~"
    for group in group_list:
        message = message+f"\n群名称："+group["group_name"]
    await search_group_list.send(message)

# -----多群广播发车功能的开启与关闭
broadcast_runcar = on_command("broadcast", permission=SUPERUSER, block=True, priority=10)
# 分析是开是关
@broadcast_runcar.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if 'on' in str(cmd):
        state['broadcast_runcar'] = True
        pm.broadcast_runcar(state['broadcast_runcar'])
        await broadcast_runcar.finish("多群广播功能打开啦！")
    elif 'off' in str(cmd):
        state['broadcast_runcar'] = False
        pm.broadcast_runcar(state['broadcast_runcar'])
        await broadcast_runcar.finish("多群广播功能关闭啦！")
    else:
        await broadcast_runcar.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')

# ----- 白名单添加与解除 -----
lihua_whitelist = on_command("lihua_wl", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@lihua_whitelist.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'add' in str(cmd):
        state['add_mode'] = True
    elif 'del' in str(cmd):
        state['add_mode'] = False
    else:
        await lihua_whitelist.finish(f'无效参数: {cmd}, 请输入 add 或 del 为参数')
# 群聊部分自动获取sid
@lihua_whitelist.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@lihua_whitelist.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await lihua_whitelist.reject(f"无效目标对象: {sid}")
    await lihua_whitelist.finish(pm.UpdateWhiteList(sid,state['add_mode']))

# ----- 黑名单添加与解除 -----
lihua_ban = on_command("lihua_ban", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@lihua_ban.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'add' in str(cmd):
        state['add_mode'] = True
    elif 'del' in str(cmd):
        state['add_mode'] = False
    else:
        await lihua_ban.finish(f'无效参数: {cmd}, 请输入 add 或 del 为参数')
# 群聊部分自动获取sid
@lihua_ban.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@lihua_ban.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await lihua_ban.reject(f"无效目标对象: {sid}")
    await lihua_ban.finish(pm.UpdateBanList(sid,state['add_mode']))


# ------- 桌游查询功能开启与关闭 -------
search_boardgame = on_command("lihua_search_boardgame", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@search_boardgame.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'on' in str(cmd):
        state['search_boardgame'] = True
    elif 'off' in str(cmd):
        state['search_boardgame'] = False
    else:
        await search_boardgame.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')
# 群聊部分自动获取sid
@search_boardgame.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@search_boardgame.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await search_boardgame.reject(f"无效目标对象: {sid}")
    await search_boardgame.finish(pm.Update_search_boardgame(sid,state['search_boardgame']))

# ------- 图包查询功能开启与关闭 -------
search_mod = on_command("lihua_search_mod", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@search_mod.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'on' in str(cmd):
        state['search_mod'] = True
    elif 'off' in str(cmd):
        state['search_mod'] = False
    else:
        await search_mod.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')
# 群聊部分自动获取sid
@search_mod.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@search_mod.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await search_mod.reject(f"无效目标对象: {sid}")
    await search_mod.finish(pm.Update_search_mod(sid,state['search_mod']))

# ------- 桌游发车功能开启与关闭 -------
run_car = on_command("lihua_run_car", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@run_car.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'on' in str(cmd):
        state['run_car'] = True
    elif 'off' in str(cmd):
        state['run_car'] = False
    else:
        await run_car.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')
# 群聊部分自动获取sid
@run_car.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@run_car.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await run_car.reject(f"无效目标对象: {sid}")
    await run_car.finish(pm.Update_run_car(sid,state['run_car']))

# ------- 桌游查车功能开启与关闭 -------
search_car = on_command("lihua_search_car", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@search_car.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'on' in str(cmd):
        state['search_car'] = True
    elif 'off' in str(cmd):
        state['search_car'] = False
    else:
        await search_car.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')
# 群聊部分自动获取sid
@search_car.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@search_car.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await search_car.reject(f"无效目标对象: {sid}")
    await search_car.finish(pm.Update_search_car(sid,state['search_car']))

# ------- 是否发送多群广播车主信息开启与关闭 -------
broadcastruncar = on_command("lihua_broadcastruncar", permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER, block=True, priority=10)
# 分析是新增还是删除
@broadcastruncar.handle()
async def cmdArg(state: T_State,cmd:Message = CommandArg()):
    if   'on' in str(cmd):
        state['broadcastruncar'] = True
    elif 'off' in str(cmd):
        state['broadcastruncar'] = False
    else:
        await broadcastruncar.finish(f'无效参数: {cmd}, 请输入 on 或 off 为参数')
# 群聊部分自动获取sid
@broadcastruncar.handle()
async def group(event:GroupMessageEvent, state: T_State):
    state['sid'] = 'group_' + str(event.group_id)
# 手动获取sid, 并调用对应的方法进行处理
@broadcastruncar.got('sid',prompt='请按照 “会话类型_会话id” 的格式输入目标对象, 例如:\ngroup_114514\nuser_1919810')
async def _(state: T_State):
    sid = str(state['sid'])
    if not verifySid(sid):
        await broadcastruncar.reject(f"无效目标对象: {sid}")
    await broadcastruncar.finish(pm.Update_broadcastruncar(sid,state['broadcastruncar']))

# 先自动审批加群信息，懒
auto_req = on_request(priority =1,  block =True)
@auto_req.handle()
async def _(bot:Bot,event : GroupRequestEvent):
    # 自动同意别人的邀请
    await event.approve(bot)




# ----------------娱乐功能
hitme = on_command("梨花揍我",block=True,priority=90)
@hitme.handle()
async def _(bot: Bot, event: Event):
    if event.get_user_id() == "739150373":
        await hitme.finish(Message(f'[CQ:at,qq={event.get_user_id()}]哥哥讨厌~不想揍哥哥'))
    else:
        await hitme.finish(Message(f'[CQ:at,qq={event.get_user_id()}]哥哥说不可以跟hentai说话（嫌弃）'))

tietie = on_command("梨花贴贴",block=True,priority=90)
@tietie.handle()
async def _(bot: Bot, event: Event):
    if event.get_user_id() == "739150373":
        await tietie.finish(Message(f'[CQ:at,qq={event.get_user_id()}]和哥哥贴贴~'))
    else:
        await tietie.finish(Message(f'[CQ:at,qq={event.get_user_id()}]梨花不和不熟悉的人贴贴！'))

kiss = on_command("梨花亲亲",block=True,priority=90)
@kiss.handle()
async def _(bot: Bot, event: Event):
    if event.get_user_id() == "739150373":
        await kiss.finish(Message(f'[CQ:at,qq={event.get_user_id()}]不可以呦！去亲嫂子去！'))
    else:
        await kiss.finish(Message(f'[CQ:at,qq={event.get_user_id()}]给梨花爬！'))