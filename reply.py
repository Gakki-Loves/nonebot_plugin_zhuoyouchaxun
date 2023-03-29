'''
Author: Gakkilove 739150373@qq.com
Date: 2023-03-20 11:34:13
LastEditors: Gakkilove 739150373@qq.com
LastEditTime: 2023-03-20 11:58:40
FilePath: \nonebot_plugin_zhuoyouchaxun\reply.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''

from nonebot.plugin.on import on_message
from nonebot.rule import to_me
from nonebot.adapters.onebot.v11 import (
    GROUP,
    MessageEvent,
    Message,
)


import re
import random


from pathlib import Path
from .player_info import player_search_nickname

from .utils import (
    hello__bot,
    hello__reply,
    get_chat_result,
    normalwords
)





talk = on_message(rule = to_me(), permission = GROUP, priority=99, block=False)
@talk.handle()
async def _(event: MessageEvent):
    # 获取消息文本
    msg = str(event.get_message())
    # 去掉带中括号的内容(去除cq码)
    msg = re.sub(r"\[.*?\]", "", msg)

    # 如果是光艾特bot(没消息返回)，就回复以下内容
    if (not msg) or msg.isspace():
        await talk.finish(Message(random.choice(hello__reply)))
    
    # 如果是打招呼的话，就回复以下内容
    if  msg in hello__bot:
            await talk.finish(Message(random.choice(hello__reply)))

    # 获取用户nickname
    playerid = event.get_user_id()
    nickname = player_search_nickname(playerid)


    # 从 LeafThesaurus 里获取结果
    if result := get_chat_result(normalwords,msg):
        await talk.finish(Message(result.replace("name", str(nickname[0][0]))))

                                                                                                                                                                                                                                                                                                                                                