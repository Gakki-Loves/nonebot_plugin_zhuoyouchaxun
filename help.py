'''
Author: Gakkilove 739150373@qq.com
Date: 2023-04-03 22:07:06
LastEditors: Gakkilove 739150373@qq.com
LastEditTime: 2023-04-04 09:07:52
FilePath: \nonebot_plugin_zhuoyouchaxun\help.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
'''
from nonebot_plugin_txt2img import Txt2Img
from nonebot import on_command
from nonebot.adapters.onebot.v11 import (
                                         MessageEvent,MessageSegment,Bot
                                         )
from nonebot.adapters.onebot.v11 import GROUP_ADMIN, GROUP_OWNER
from nonebot.permission import SUPERUSER
from nonebot.typing import T_State

# -----------------------复用功能-----------------------
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







# -----------------------帮助菜单-----------------------
# 普通命令
lihuahelp = on_command("梨花命令",block=True, priority=10,aliases={"梨花指令","梨花帮助文档","梨花酱 指令","梨花酱指令","梨花帮助","梨花文档","梨花help"})
@lihuahelp.handle()
async def _():
    help_title = """梨花的使用命令:"""
    help_msg = """
    桌游功能：          
    ‘桌游查询 XXX’       查询XXX桌游信息
    ‘图包查询 XXX’       查询XXX图包信息
    ‘桌游查车’/‘查车’    查询正在进行的桌游车
    ‘桌游发车’/‘发车’    你来开一辆车
    ‘桌游封车’/‘封车’    只可以封自己发的车车哦
    ‘上传图包’           把你的图包链接上传至数据库
    (发送”桌游发车“梨花可以把你的约车信息广播到几十个群哦)

    个人信息功能：
    （仍在开发，涉及到后续的金币系统和梨花好感度系统）
    ‘玩家初始化’        初始化你的个人信息
    ‘修改昵称’          修改梨花对你的称谓
    ‘查询个人信息’      康康你和梨花的好感度是多少吧！

    其他功能：
    ‘XX天气’        查询XX未来几天的天气
    ‘占卜/塔罗牌’   占卜功能（暂时停用）
    ‘人生重开’      人生重开模拟器（暂时停用）
    ‘疯狂星期四’    随机发送疯狂星期四文案（暂时停用）
    ‘.send +内容’   可以直接和bot作者对话，提出意见建议
    ‘赞助梨花’       给梨花买一杯奶茶叭！

    其他命令：
    ‘梨花管理员命令’  各群管理员可通过此命令对某个功能开启或关闭
    ‘梨花超级用户命令’  哥哥专用，有一些额外的功能
    ‘梨花权限命令’      哥哥专用，可以直接开关某个群的某个插件
    """
    # 渲染成图片
    help_msg = msg_word2pic(help_title,help_msg)

    await lihuahelp.finish(help_msg)

# 管理员命令
lihua_cmdhelp = on_command("梨花管理员命令",permission=GROUP_ADMIN|GROUP_OWNER|SUPERUSER,block=True, priority=10,aliases={"梨花管理员指令","梨花管理员帮助文档","梨花酱 管理员指令","梨花酱管理员指令","梨花管理员帮助","梨花管理员文档","梨花管理员help","梨花help管理员"})
@lihua_cmdhelp.handle()
async def _():
    help_title = """梨花的管理员命令:"""
    help_msg = """
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
    # 渲染成图片
    help_msg = msg_word2pic(help_title,help_msg)
    await lihua_cmdhelp.finish(help_msg)

lihua_superhelp = on_command("梨花超级用户命令",permission=SUPERUSER,priority=11)
@lihua_superhelp.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):

    help_msg = """
    桌游功能：          
    ‘桌游查询 XXX’       查询XXX桌游信息
    ‘图包查询 XXX’       查询XXX图包信息
    ‘桌游查车’/‘查车’    查询正在进行的桌游车
    ‘桌游发车’/‘发车’    你来开一辆车
    ‘桌游封车’/‘封车’    只可以封自己发的车车哦
    ‘上传图包’           把你的图包链接上传至数据库
    (发送”桌游发车“梨花可以把你的约车信息广播到几十个群哦)

    个人信息功能
    （仍在开发，涉及到后续的金币系统和梨花好感度系统）
    “玩家初始化”        初始化你的个人信息
    “修改昵称”          修改梨花对你的称谓
    “查询个人信息”      康康你和梨花的好感度是多少吧！

    其他功能：
    ‘XX天气’        查询XX未来几天的天气
    ‘占卜/塔罗牌’   占卜功能（暂时停用）
    ‘人生重开’      人生重开模拟器（暂时停用）
    ‘疯狂星期四’    随机发送疯狂星期四文案（暂时停用）
    ‘.send +内容’   可以直接和bot作者对话，提出意见建议

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
    
    超级用户功能：
    ‘状态/status’   查看服务器状态
    ‘图包删除’      删除某个图包
    ‘查看群列表’    查看梨花加入的群
    ‘梨花权限命令’    管理插件权限
    ‘查询图包数量’    查询梨花图书馆收录了多少个图包
    ‘查询玩家数量’    查询梨花图书馆有多少小伙伴登记在册
    ‘查询图包上传者’   查询某图包是谁上传的
    
    """
    title = '梨花超级用户命令:'
    text = help_msg
    font_size = 20
    txt2img = Txt2Img()
    txt2img.set_font_size(font_size)
    pic = txt2img.draw(title, text)
    msg = MessageSegment.image(pic)
    await lihua_superhelp.send(msg)


lhpm = on_command("梨花权限命令",permission=SUPERUSER,priority=11)
@lhpm.handle()
async def _(bot: Bot, event: MessageEvent,state:T_State):

    help_msg = """
    lhpm ls：                      查看当前会话插件列表
    -u <user_id>, --user <user_id>    查看指定用户插件列表
    -g <group_id>, --group <group_id> 查看指定群插件列表
    -a, --all                      查看所有插件
    
    lhpm block <plugin ...>        禁用当前会话插件
    plugin ...                     必选参数，需要禁用的插件名
    -a, --all                      全选插件
    -r, --reverse                  反选插件
    -u <user_id ...>, --user <user_id ...>    管理指定用户设置
    -g <group_id ...>, --group <group_id ...> 管理指定群设置（仅超级用户可用）

    lhpm unblock <plugin ...>      启用当前会话插件（需要权限）
    plugin ...                     必选参数，需要禁用的插件名
    -a, --all                      全选插件
    -r, --reverse                  反选插件
    -u <user_id ...>, --user <user_id ...>    管理指定用户设置（仅超级用户可用）
    -g <group_id ...>, --group <group_id ...> 管理指定群设置（仅超级用户可用）
    """
    title = '梨花权限命令:'
    text = help_msg
    font_size = 20
    txt2img = Txt2Img()
    txt2img.set_font_size(font_size)
    pic = txt2img.draw(title, text)
    msg = MessageSegment.image(pic)
    await lhpm.send(msg)
