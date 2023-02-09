"""
Author: Gakkilove 739150373@qq.com
Date: 2023-02-09 23:32:23
LastEditors: Gakkilove 739150373@qq.com
LastEditTime: 2023-02-09 23:33:04
FilePath: \nonebot_plugin_zhuoyouchaxun\player_info.py
Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
"""

# +------------------------import区-------------------------+
import os
import sqlite3
from pathlib import Path
from datetime import datetime








# +------------------------逻辑区-------------------------+

# -----初始化玩家信息
def player_init(player_id,player_name):
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO player VALUES('{player_id}','{player_name}','0','0')"
    ) 
    #提交事务
    conn.commit()
    conn.close()

# -----判断玩家信息是否存在
def player_exist(player_id):
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"SELECT player_id from player WHERE player_id like '{player_id}' "
    ) 
    db_data = cur.fetchall()
    #提交事务
    conn.commit()
    conn.close()
    if db_data:
            return True
    else:
            return False

# -----修改昵称
def player_rename(player_id,rename):
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"UPDATE player SET player_name = '{rename}' WHERE player_id = '{player_id}' "
    ) 
    #提交事务
    conn.commit()
    conn.close()