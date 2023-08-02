'''
Author: Gakkilove 739150373@qq.com
Date: 2023-02-11 22:20:48
LastEditors: Gakkilove 739150373@qq.com
LastEditTime: 2023-04-06 10:48:39
FilePath: \nonebot_plugin_zhuoyouchaxun\__init__.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''



from nonebot import require
require("nonebot_plugin_apscheduler")
from nonebot_plugin_apscheduler import scheduler

import asyncio
from nonebot import on_command,on_notice,on_request,on_fullmatch

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
from nonebot_plugin_txt2img import Txt2Img
import sqlite3
from pathlib import Path
import asyncio
import os
import json
from datetime import datetime
from nonebot.typing import T_State
from nonebot.log import logger
from nonebot.exception import ActionFailed
from nonebot.permission import SUPERUSER
from .permission_manager import PermissionManager

from  nonebot . params  import  Arg ,  CommandArg ,  ArgPlainText 
from .get_data import *
from .player_info import player_init,player_exist,player_rename,player_search_info,player_search_nickname
from .reply import talk
# from .friendship import sign
from .help import *

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

# 渲染成图片发送
def msg_word2pic(wordtitle,wordmsg):
    title = wordtitle
    text = wordmsg
    font_size = 20
    txt2img = Txt2Img()
    txt2img.set_font_size(font_size)
    pic = txt2img.draw(title, text)
    picmsg = MessageSegment.image(pic)
    return picmsg




# --------------发送查询信息部分-----------------
# 桌游查询的正则表达式
chaxun = on_regex(
    chaxun_regex,
    priority=20,
    block=True,
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

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)



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

    # 尝试发送
    try:
        if state['ifchaxun'] == True:
            if isinstance(event, PrivateMessageEvent):
                #msglist = message_list[0][0]
                #test_str = "".join(msglist)
                #test_str = "".join(test_str)
                #picmsg = msg_word2pic("",test_str)
                #await chaxun.send(picmsg)
                for msg in message_list:
                    await chaxun.send(msg)
                    #await asyncio.sleep(0.5)
            elif isinstance(event, GroupMessageEvent):
                #for msg in message_list:
                    #await chaxun.send(msg)
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
        elif state['ifchaxun'] == False:
            for msg in message_list:
                    #await chaxun.send(msg)
                    await chaxun.finish(msg)
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
        await tubao.finish("图包查询功能没有开启哦~")

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)

    
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
                '''for msg in message_list:
                    await tubao.send(msg)
                    await asyncio.sleep(0.5)
                # 这里是群聊转发的方式，现在已经不能用了，仅仅是保留代码'''
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
            '''for msg in message_list:
                #await chaxun.send(msg)
                await tubao.send(msg)
                await asyncio.sleep(0.5)'''
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
run_car = on_command("桌游发车",priority=10,aliases={"发车"})

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

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)

    # 判定一下司机是否已经有一辆车在开了
    data = ifcarexist(playerid)
    if data == False:
         await run_car.finish("一个人不可以同时开两辆车车哦！请封车后再开！")



    # 用state字典把这里获取的 user_id、昵称保存
    #playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
    playername = player_search_nickname(playerid)
    state['userid'] = str(event.user_id)
    state['playername'] = str(playername[0][0])
    await run_car.send("请输入发车信息，例如：\n《桌游名》（是否带扩）\n【人数&教学】X=X/带教学\n【类型】美式/战斗\n【时长】教15分钟；玩60分钟\n【难度】2/5\n【房名&密码】XXX/xxxx\n【语音】https://kook.top/XXX\nPS： 这是一辆车车的模板")

@run_car.got("content")
async def _(state:T_State,content: str = ArgPlainText("content"),prompt="模板"):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['content'] = content
    await run_car.send("请输入截止时间~例如“21:50”")


@run_car.got("deadline")
async def _(bot: Bot,state:T_State,event: MessageEvent,deadline: str = ArgPlainText("deadline")):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['deadline'] = deadline
    deadline = deadline.replace("：", ":")
    matchObj = re.match(r"^([0-9]|1[0-9]|2[0-3]|0[0-9]):([0-9]|[1-5]\d|0[0-9])$", deadline, re.I)#正则表达式，来检验AA:BB这样的时间，其中AA的范围是0-23和00-23，BB的范围是00-59和0-59
    if(matchObj!=None):# 如果上面这个re.match函数匹配到东西了，也就是matchObj的结果不为None那说明用户输入的时间是正确的
        timeArray = time.strptime(deadline, "%H:%M") # 把用户输入的时间拆分为小时和分钟，以便于后续把9:31这样的“少0”的时间变成正常的XX:XX格式的时间
        hour=timeArray[3] # 小时
        min=timeArray[4] # 分钟
        if(hour>=0 and hour<=9): #
            deadline='0'+str(hour)+":" # 把0-9点前面加0，这步结束deadline的值应该是变成00，01，02，···，09
        else:
            deadline=str(hour)+":"# 如果小时是11-23那就不管，这步结束deadline的值应该是变成10，11，12，···，23
        if(min>=0 and min<=9): 
            deadline=deadline+'0'+str(min) # 把0-9分前面加0
        else:
            deadline+=str(min)
        if "24:00">=deadline>="00:00":# 虽然根据"^[0-23]{1,2}:[0-59]{1,2}$"这个正则表达式，只要能进到if(matchObj!=None):里的时间，都肯定符合"24:00">=deadline>="00:00"这个要求，但为了不删除Gakki的代码，还是把这句话保留下来了
            now = datetime.now()
            time_now = now.strftime('%H:%M')
            if deadline >= time_now:
                car_id = str(state['userid'])
                content = str(state['content'])
                runcar(car_id,content,deadline)
            else:
                await run_car.finish("笨蛋！发车时间怎么能比现在时间还早！请输入“桌游发车”重新操作哦~")
        else :
            await run_car.finish("敲你脑袋哦！时间填错啦！请输入“桌游发车”重新操作哦~")
    else:
        await run_car.finish("敲你脑袋哦！时间填错啦！请输入“桌游发车”重新操作哦~")
    #await run_car.finish("发车成功！（现阶段私聊发车没办法全群广播噢！只能输入“查车”来看现在有什么车）")
    # ------多群广播发车信息功能（暂时关闭）
    cmd_broad_cast = pm.Query_broadcast_runcar()
    #cmd_broadcast = pm.Query_broadcastruncar(state['sid'])
    group_list = await bot.get_group_list()

    # ---写进garage库部分
    now= str(time.strftime('%Y-%m-%d %a %H:%M:%S'))
    # 获取字典内容，不要问我为什么不用上面的变量因为我懒
    player_id = str(state['userid'])
    content = str(state['content'])
    group_id = str(event.group_id)
    playername = str(state['playername'])
    add_garage(player_id,content,group_id,now)
    # ---写进garage库部分


    # 判断是否为主群
    group_id = str(event.group_id)
    if group_id == "177053575" :
    # if group_id == "373939194":
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
                    await bot.send_group_msg(group_id=group["group_id"], message=(content+"\n【截止时间】"+deadline+"\n【发车人】"+playername+"\n这条是多群广播信息，第二轮测试期间，发车信息被多群广播只有在梨花的图书馆（群号：177053575）才可以使用哦！"))
                    await asyncio.sleep(1)
            await run_car.finish(f"梨花一共加入了{allGroupNum}个群，已经帮您广播转发到了{onBroadCastGroupNum}个群，其余群关闭了接收广播功能~")
        elif cmd_broad_cast == False:
            await run_car.finish("多群广播功能没有开启呦~梨花已经帮你记录到车库啦！")
        else:
            await run_car.finish("多群广播设置不正确哦！")
    else:
        await run_car.finish("梨花已经帮你记录到车库啦！\n(第二轮测试期间，发车信息被多群广播只有在梨花的图书馆（群号：177053575）才可以使用哦！)")

# -写进garage库部分,前面finish了把内容前移吧，就不再用一个matcher了
'''@run_car.handle()
async def _(bot: Bot, event: GroupMessageEvent,state:T_State):
    # 获取现在的时间
    now= str(time.strftime('%Y-%m-%d %a %H:%M:%S'))
    # 获取字典内容
    player_id = str(state['userid'])
    content = str(state['content'])
    group_id = str(event.group_id)
    add_garage(player_id,content,group_id,now)
    await run_car.finish()'''

# ----------------------预约发车------------------------------
reserve_car = on_command("预约发车",priority=10,permission=SUPERUSER)

@reserve_car.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):

    # 判断是否为主群，不是主群不开这个功能
    group_id = str(event.group_id)
    if group_id == "177053575" :
    # if group_id == "373939194":
        pass
    else:
        await reserve_car.finish("预约发车目前为测试功能，只有在梨花的图书馆（群号：177053575）才可以使用哦！")

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)

    # 获取预约发车信息
    playername = player_search_nickname(playerid)
    state['userid'] = str(event.user_id)
    state['playername'] = str(playername[0][0])
    await reserve_car.send("这是一辆未来之车，请输入发车信息：\n《桌游名》（是否带扩）\n【人数&教学】X=X/带教学\n【类型】美式/战斗\n【时长】教15分钟；玩60分钟\n【难度】2/5\n【联系方式】QQ/微信/其他\n")

@reserve_car.got("content")
async def _(state:T_State,content: str = ArgPlainText("content"),prompt="模板"):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['content'] = content
    await reserve_car.send("请输入未来的发车时间，时间格式为：\n月(01-12)-日(01-31) 小时(00-24):分钟(00-60),例如:\n05-01 08:00\nPS：请务必使用上述格式，否则系统无法识别")

@reserve_car.got("deadline")
async def _(bot: Bot,state:T_State,event: GroupMessageEvent,deadline: str = ArgPlainText("deadline")):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['deadline'] = deadline
    deadline = deadline.replace("：", ":")
    matchObj = re.match(r"^([0-9][0-9]-[0-9][0-9]\s[0-9][0-9]\S[0-9][0-9])", deadline, re.I)#正则表达式，来检验AA:BB这样的时间，其中AA的范围是0-23和00-23，BB的范围是00-59和0-59
    if(matchObj!=None):# 如果上面这个re.match函数匹配到东西了，也就是matchObj的结果不为None那说明用户输入的时间是正确的
        timeArray = time.strptime(deadline, "%m-%d %H:%M") # 把用户输入的时间拆分为小时和分钟，以便于后续把9:31这样的“少0”的时间变成正常的XX:XX格式的时间
        hour=timeArray[3] # 小时
        min=timeArray[4] # 分钟
        month = timeArray[1] # 月份
        day = timeArray[2] # 日期
        if(month>=0 and hour<=9): #
            deadline='0'+str(month)+"-" 
        else:
            deadline=str(month)+"-"
        if(day>=0 and day<=9): #
            deadline+='0'+str(day)+" " 
        else:
            deadline+=str(day)+" "
        if(hour>=0 and hour<=9): #
            deadline+='0'+str(hour)+":" # 把0-9点前面加0，这步结束deadline的值应该是变成00，01，02，···，09
        else:
            deadline+=str(hour)+":"# 如果小时是11-23那就不管，这步结束deadline的值应该是变成10，11，12，···，23
        if(min>=0 and min<=9): 
            deadline=deadline+'0'+str(min) # 把0-9分前面加0
        else:
            deadline+=str(min)
        
        now = datetime.now()
        time_now = now.strftime('%m-%d %H:%M')
        if deadline >= time_now:
            car_id = str(state['userid'])
            content = str(state['content'])
            reservecar(car_id,content,deadline)
        else:
            await run_car.finish("笨蛋！发车时间怎么能比现在时间还早！请输入“桌游发车”重新操作哦~")
        
    else:
        await run_car.finish("敲你脑袋哦！时间填错啦！请输入“桌游发车”重新操作哦~")


    # ---写进garage库部分
    now= str(time.strftime('%Y-%m-%d %a %H:%M:%S'))
    # 获取字典内容，不要问我为什么不用上面的变量因为我懒
    player_id = str(state['userid'])
    content = str(state['content'])
    group_id = str(event.group_id)
    add_garage(player_id,content,group_id,now)
    # ---写进garage库部分


    await reserve_car.finish("梨花已经帮你记录到车库啦！可以输入“查预约车”命令来查询呦")




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

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)
        
    # 用state字典把这里获取的user_id保存
    message_searchcar = searchcar()
    
    
    # -----消息发送列表
    message_list = []
    # 先把常规车库加入
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
    # 20230725更新，在查车时直接查询发车人昵称
    # 使用车车信息里的qq号进行查询
    try:
        if isinstance(event, PrivateMessageEvent):
            msg = []
            for msg in message_list:
                #await chaxun.send(msg)
                await search_car.send(msg)
                await asyncio.sleep(0.5)
        elif isinstance(event, GroupMessageEvent):
            '''msg = []
            for msg in message_list:
                #await chaxun.send(msg)
                await search_car.send(msg)
                await asyncio.sleep(0.5)'''
            #title = ' '
            #text = message_list
            #font_size = 20
            #txt2img = Txt2Img()
            #txt2img.set_font_size(font_size)
            #pic = txt2img.draw(title, text)
            #msg = MessageSegment.image(pic)

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
# -----------------------查预约车-----------------------
search_car = on_command("查预约车",permission=SUPERUSER,block=True,priority=11,aliases={"查未来车"})
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

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)
        
    # 用state字典把这里获取的user_id保存
    message_searchreservecar = search_reservecar()
    
    
    # -----消息发送列表
    message_list = []
    # 先把常规车库加入
    for car_list in message_searchreservecar:
        # 如果idname0的状态为True，说明有这个信息
        if car_list[0]:               
            message = f"下面是存在的未来之车~"
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
            #title = ' '
            #text = message_list
            #font_size = 20
            #txt2img = Txt2Img()
            #txt2img.set_font_size(font_size)
            #pic = txt2img.draw(title, text)
            #msg = MessageSegment.image(pic)

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


# -----

# ----------------------封车------------------------------
deletecar = on_command("强制封车",permission=SUPERUSER,priority=11)
@deletecar.handle()
async def _(bot: Bot, event: PrivateMessageEvent,state:T_State):
    state['player_id'] = event.get_user_id()
    await deletecar.send("请输入需要封车的车车ID")

@deletecar.got("car_id")
async def _(state:T_State,car_id: str = ArgPlainText("car_id"),prompt="模板"):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    player_id = str(state['player_id'])
    car_id = int(car_id)
    msg_list = delete_car(car_id,player_id)
    if msg_list[0]:
        await deletecar.finish(msg_list[1])
    else:
        await deletecar.finish(msg_list[1])


# ----------------------封车（不需要输入id版）------------------------------
deletecar2 = on_command("桌游封车",priority=11,aliases={"封车"})
@deletecar2.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    player_id = event.get_user_id() #根据车车的qq号封
    msg_list = delete_car2(player_id)
    if msg_list[0]:
        await deletecar2.finish(msg_list[1])
    else:
        await deletecar2.finish(msg_list[1])




# ----------------------上传图包------------------------------
upload_mod = on_fullmatch("上传图包",priority=10)

@upload_mod.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):

    ## 开启关闭功能写不写，谁会拒绝上传图包呢
    # 功能开启判定
    #if isinstance(event, PrivateMessageEvent):
        #state['sid'] = 'user_' + str(event.user_id)
    #if isinstance(event, GroupMessageEvent):
        #state['sid'] = 'group_' + str(event.group_id)
    #cmd_search_boardgame = pm.Query_run_car(state['sid'])
    #if cmd_search_boardgame == False:
        #await chaxun.finish("桌游发车功能没有开启哦~")

    # 进行梨花身份信息的创建
    playerid = event.get_user_id()
    info = player_exist(playerid)
    if info:
        pass
    else:
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)
        
    # 用state字典把这里获取的user_id保存
    state['upload_id'] = str(event.user_id)
    await upload_mod.send("请输入你上传图包的图包名字\n例如“王权骰铸/瞎几把投/侠技霸骰”\n（PS：可以把你知道的别名都写上去哦~）")

@upload_mod.got("mod_name")
async def _(state:T_State,mod_name: str = ArgPlainText("mod_name"),prompt="模板"):
    # 获取刚刚获得的user_id，这样就能跨函数使用
    #car_id = str(state['userid'])
    state['mod_name'] = mod_name
    await upload_mod.send("请输入图包的网盘链接~\n例如“https://share.weiyun.com/CQOzyNx4”")


@upload_mod.got("link")
async def _(bot: Bot,state:T_State,event: MessageEvent,link: str = ArgPlainText("link")):
    #获取刚刚获得的上传人id和图包名字
    mod_name = str(state['mod_name'])
    upload_id = str(state['upload_id'])
    uploadmod(upload_id,mod_name,link)
    await upload_mod.send("上传图包完毕~感谢你为桌游图书馆做出的贡献~")
    # ------
    # 这里其实可以加一个对link的正则匹配，得是https://开头的（网盘应该不会有http协议）
    # ------

    

# ----------------------图包删除------------------------------
deletemod = on_command("图包删除",priority=11,aliases={"删除图包"},permission=SUPERUSER)
@deletemod.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    await deletemod.send("请输入需要删除的图包ID")

@deletemod.got("mod_id")
async def _(state:T_State,mod_id: str = ArgPlainText("mod_id"),prompt="图包ID"):
    mod_id = int(mod_id)
    msg_list = delete_mod(mod_id)
    await deletemod.finish("梨花已经把图包已经删除咯~")



# ----------------------查询图包数量------------------------------
searchmodcount = on_command("查询图包数量",priority=99,permission=SUPERUSER)
@searchmodcount.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    data = search_mod_count()
    await searchmodcount.send(f"梨花查询了一下，目前图包库有 {data[0][0]} 个图包呦~")


# ----------------------查询玩家数量------------------------------
searchplayercount = on_command("查询玩家数量",priority=99,permission=SUPERUSER)
@searchplayercount.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    data = search_player_count()
    await searchplayercount.send(f"梨花查询了一下，目前已有{data[0][0]}名玩家登记在册呦~")

# ----------------------查询图包上传者------------------------------
searchmoduploader = on_command("查询图包上传者",priority=99,permission=SUPERUSER)
@searchmoduploader.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):
    await deletemod.send("请输入需要查询的图包ID")

@searchmoduploader.got("moduploadid")
async def _(state:T_State,moduploadid: str = ArgPlainText("moduploadid"),prompt="图包ID"):
    moduploadid = int(moduploadid)
    uploader = search_mod_uploader(moduploadid)
    await deletemod.finish(f"梨花查询了图包库，图包上传者是 {uploader[0][4]} 哦~")

# ----------------------随机桌游------------------------------+
# 随机发送一个图包
randam_boardgame = on_command("随机桌游",priority=50)
@randam_boardgame.handle()
async def _(bot: Bot, event: PrivateMessageEvent,state:T_State):
    message_list = []
    radam_data = randamboardgame()

    # 尝试发送
    try:
        for msg in radam_data:
            await randam_boardgame.send(msg)
            await asyncio.sleep(0.5)
    #若发送失败
    except ActionFailed as F:
        logger.warning(F)
        await randam_boardgame.finish(
            message=Message(f"不听不听，哄我两句再试试！"),
            at_sender=True
        )







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
@scheduler.scheduled_job('cron', hour='1')
async def _():
    clear_table()
    
# -----------------------cheche表每天删除-----------------------





# ------------------欢迎新群友----------------
# -初始化
notice_handle  = on_notice ( priority =5,  block =True ) 

@notice_handle.handle () 
async  def  GroupNewMember ( bot :  Bot ,  event :  GroupIncreaseNoticeEvent ): 

    path_record = Path(__file__).parent /'resource'/ "入群语音.mp3"
    record = MessageSegment.record(path_record)
    if  event . user_id  == event . self_id : 
        await  bot . send_group_msg ( group_id =event . group_id ,  message =Message ( 
            MessageSegment . text ( '小伙伴们好呀~我是梨花酱，是桌游图书馆的管理员哦~\n' ) ) )
    else:
        await bot.send_group_msg ( group_id =event . group_id ,  message =Message ( 
            MessageSegment . at ( event . user_id )  
            + MessageSegment . text ( "欢迎新桌友哦~我是桌游图书馆管理员梨花酱，请注意查看群公告内容~梨花可以帮你查找图包，向几十个群发送您的约车信息~发送“梨花命令”四个字可以获得梨花的命令目录哦~\n" )
            ))
        await notice_handle.send(record)
            #await bot.send_group_msg(group_id =groupid,message =Message (record))
    



# -----------------------------------------------------------------------------------
# -------------------------------- 权限管理部分 --------------------------------------
# -----------------------------------------------------------------------------------

#------------------------超级用户权限-------------------------
# -----查看群列表（超级用户专用）
search_group_list = on_command("查看群列表",permission=SUPERUSER)
@search_group_list.handle()
async def _(bot: Bot, event: PrivateMessageEvent):
    group_list = await bot.get_group_list()
    message = f"梨花已加入的群~"
    try:
        for group in group_list:
            message = message+f"\n群名称："+group["group_name"]

        #测试list渲染
        test_str = "".join(message)
        picmsg = msg_word2pic("",test_str)
        await search_group_list.send(picmsg)
    except ActionFailed as F:
        logger.warning(F)
        await search_car.finish(
            message=Message(f"不听不听，哄我两句再试试！"),
            at_sender=True
        )



    #for group in group_list:
       # message = message+f"\n群名称："+group["group_name"]
    #await search_group_list.send(message)

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

# -----自动审批加群信息
# 读取关键词列表
with open('data/LihuaBot/keywords.json', 'r', encoding='utf-8') as f:
    KEYWORDS = json.load(f)['keywords']

auto_req = on_request()
@auto_req.handle()
async def _(bot:Bot,event : GroupRequestEvent):
    group_id = str(event.group_id)
    if group_id == "177053575":
        raw  = json . loads ( event . json ()) 
        gid  = str ( event . group_id ) 
        flag  = raw ['flag' ]
        sub_type  = raw ['sub_type' ]
        logger . info ( 'flag:' ,  str ( flag )) 
        if  sub_type  == 'add' : 
            uid  = event . user_id 
            comment  = raw ['comment' ]
            word  = re . findall ( re . compile ( '答案：(.*)'),  comment ) 
            text = comment.strip()
            if any(keyword in text for keyword in KEYWORDS):
                logger . info ( f"同意{uid }加入群 {gid },验证消息为 “{text}”") 
                await bot.set_group_add_request(flag =flag , 
                    sub_type =sub_type , 
                    approve =True , 
                    reason =' ' , )
                await  bot . send_msg ( user_id =int ( "739150373"),  message =f"同意{uid }加入群 {gid },验证消息为 “{word }”") 


# +------------------------娱乐区-------------------------+
sponsor = on_fullmatch("赞助梨花",priority=99)
@sponsor.handle()
async def _(bot: Bot, event: MessageEvent):
    path = Path(__file__).parent /'resource'/ "赞助梨花.png"
    # 构造图片消息段
    image = MessageSegment.image(path)
    # 发送图片
    await sponsor.finish(image)

  
"""hitme = on_command("梨花揍我",block=True,priority=90)
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
        await kiss.finish(Message(f'[CQ:at,qq={event.get_user_id()}]给梨花爬！'))"""





# +------------------------玩家信息区-------------------------+
# -----玩家初始化
playerinit = on_fullmatch("玩家初始化",priority=90)
@playerinit.handle()
async def _(bot: Bot, event: Event):
    playerid = event.get_user_id()
    playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
    # 这里要写一个正则匹配，如果名字全是空白字符，自动给他一个昵称“喂”
    ns =player_exist(playerid)
    if ns:
        await playerinit.finish("您已经创建过玩家信息啦")
    else:
        player_init(playerid,playername)
        await playerinit.finish("已经帮您创建好玩家信息了哦~")


# -----玩家修改昵称
playerrename = on_fullmatch("修改昵称",priority=90)
@playerrename.handle()
async def _(bot: Bot, event: MessageEvent,state: T_State):
    playerid = event.get_user_id()
    state['playerid'] = playerid
    await playerrename.send("请输入修改后的昵称")

@playerrename.got("rename")
async def _(state:T_State,rename: str = ArgPlainText("rename"),prompt="rename"):
    # 获取刚刚获得的playerid，这样就能跨函数使用
    #car_id = str(state['userid'])
    playerid =state['playerid']
    player_rename(playerid,rename)
    await run_car.finish(f"您的新昵称{rename}已修改完毕~")

# -----查询个人信息
playersearchinfo = on_fullmatch("查询个人信息",priority=90)
@playersearchinfo.handle()
async def _(bot: Bot, event: MessageEvent,state: T_State):
    playerid = event.get_user_id()
    state['playerid'] = playerid
    data = player_search_info(playerid)
    if data:
        msg = f"昵称：{data[0][1]}\n金币：{data[0][2]}\n梨花好感度：{data[0][3]}\n"
        await playersearchinfo.finish(msg)
    else:
        # 没创建，帮他创建一个
        playername = json.loads(json.dumps(await bot.get_stranger_info(user_id =int(playerid))))['nickname']
        player_init(playerid,playername)
        await playersearchinfo.send("您还没有注册过玩家信息哦~\n梨花已经帮您注册啦，请再次查询~")








