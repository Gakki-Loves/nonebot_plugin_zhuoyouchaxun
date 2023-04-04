'''
Author: Gakkilove 739150373@qq.com
Date: 2023-03-29 15:16:08
LastEditors: Gakkilove 739150373@qq.com
LastEditTime: 2023-03-29 19:32:31
FilePath: \nonebot_plugin_zhuoyouchaxun\friendship.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from nonebot import on_keyword
from nonebot.adapters.onebot.v11 import GROUP, GroupMessageEvent
from nonebot.log import logger

sign = on_keyword("签到", permission=GROUP, priority=99, block=True)
@sign.handle()
async def  _(event: GroupMessageEvent):
    user_id = event.user_id
    group_id = event.group_id
    logger.opt(colors=True).info(f"群 <y>{group_id}</y> : 用户 <y>{user_id}</y> 签到")


