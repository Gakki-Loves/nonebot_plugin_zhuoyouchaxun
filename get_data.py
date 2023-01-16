#'''
#Author: Gakkilove 739150373@qq.com
#Date: 2023-01-14 11:02:34
#LastEditors: Gakkilove 739150373@qq.com
#LastEditTime: 2023-01-14 11:09:51
#FilePath: \nonebot_plugin_zhuoyouchaxun\get_data.py
#Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
#'''



import os
import asyncio
import nonebot
import sqlite3
from httpx import AsyncClient
from pathlib import Path
#from nonebot.log import logger
error = "Error:"



#返回列表，内容为桌游id和桌游名称
def get_idname(name)-> list:
    data = []
    msg_list = []
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    # 通过cur.execute执行sql语句，操作数据库
    cursor = cur.execute(
        f"SELECT BGId,BGName from main WHERE BGName like '%{name}%' "
    )
    # 得到查询结果
    db_data = cur.fetchall()

    # 断开数据库连接
    conn.close()

    # 如果没有结果
    if db_data == []:
        data.append([False,error, f"数据库中没有搜到关于{name}的信息。"])
        return data
    else:
        data.append(True)
        for i in range(len(db_data)):
            msg = (
                db_data[i][0]
                + ":"
                + db_data[i][1]
                + "\n"
            )
            msg_list.append(msg)
        data.append(msg_list)
        return [data]

# 桌游具体信息查询，参数为桌游ID
def get_BGinfo(bgid):
    data = []
    msg_list = []
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    # 通过cur.execute执行sql语句，操作数据库
    cursor = cur.execute(
        f"SELECT * from main WHERE BGId like '{bgid}' "
    )
    # 得到查询结果
    db_data = cur.fetchall()

    # 断开数据库连接
    conn.close()

        # 如果没有结果
    if db_data == []:
        data.append([False,error, f"数据库中没有搜到桌游ID:{bgid}的信息。"])
        return data
    else:
        data.append(True)
        msg = (
            "桌游ID:"+ db_data[0][0]
            + "\n桌游名称:"+ db_data[0][1]
            + "\n游戏模式:"+ db_data[0][2]
            + "\n游戏分类:"+ db_data[0][3]
            + "/"+ db_data[0][4]
            + "\n人均时长:"+ db_data[0][5]
            + "\n上手难度:"+ db_data[0][6]
            + "\n集石评分:"+ db_data[0][7]
            + "\n简介:"+ db_data[0][8]
            + "\n集石链接:"+ db_data[0][9]
            + "\nBGGid:"+ db_data[0][10]
            + "\nBGG链接:"+ db_data[0][11]
        )
        data.append(msg)
        return [data]

#查询图包信息，返回参数为图包id和图包名称
def get_tubaoname(tubao_name):
    data = []
    msg_list = []
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    # 通过cur.execute执行sql语句，操作数据库
    cursor = cur.execute(
        f"SELECT tubao_id,tubao_name, file_name  from tubao WHERE (tubao_name like '%{tubao_name}%' or file_name like '%{tubao_name}%' ) "
    )
    # 得到查询结果
    db_data = cur.fetchall()

    # 断开数据库连接
    conn.close()

    # 如果没有结果
    if db_data == []:
        data.append([False,error, f"数据库中没有搜到关于{tubao_name}的信息。"])
        return data
    else:
        data.append(True)
        for i in range(len(db_data)):
            msg = (
                db_data[i][0]
                + ":"
                + db_data[i][2]
                + "\n"
            )
            msg_list.append(msg)
        data.append(msg_list)
        return [data]


