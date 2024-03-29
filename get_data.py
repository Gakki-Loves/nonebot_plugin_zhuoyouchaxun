#'''
#Author: Gakkilove 739150373@qq.com
#Date: 2023-01-14 11:02:34
#LastEditors: Gakkilove 739150373@qq.com
#LastEditTime: 2023-01-14 11:09:51
#FilePath: \nonebot_plugin_zhuoyouchaxun\get_data.py
#Description: 这是默认设置,请设置`customMade`, 打开koroFileHeader查看配置 进行设置: https://github.com/OBKoro1/koro1FileHeader/wiki/%E9%85%8D%E7%BD%AE
#'''



import os
#import asyncio
#import nonebot
import sqlite3
from httpx import AsyncClient
from pathlib import Path
#from nonebot.log import logger
error = "出错啦！"
from datetime import datetime
from nonebot import utils
from .player_info import player_search_info
import re

def query(sql_str):
    conn = sqlite3.connect(
        Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
# 创建游标
    cur = conn.cursor()
# 通过cur.execute执行sql语句，操作数据库
    cursor = cur.execute(
        sql_str
    )
# 得到查询结果
    db_data = cur.fetchall()
# 断开数据库连接
    conn.close()
    return db_data

#返回列表，内容为桌游id和桌游名称
def get_idname(name):
    data = []
    msg_list = []
    db_data = query(f"SELECT BGId,BGName from boardgame WHERE BGName like '%{name}%' ")
    # 如果没有结果
    try:
        if db_data == []:
            data.append([False,error, f"图书馆里中没有搜到关于{name}的信息啦~请告诉梨花其他的名字或英文~"])
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
    except:
        return [False,error, f"查询失败啦！是不是命令记得不清楚呀？发送“梨花命令”这四个字查看所有命令哦~"]

# 桌游具体信息查询，参数为桌游ID
def get_BGinfo(bgid):
    data = []
    db_data = query(f"SELECT * from boardgame WHERE BGId like '{bgid}' ")
    # 如果没有结果
    try:
        if db_data == []:
            data.append([False,error, f"梨花酱没有搜到桌游ID:{bgid}的信息~要认真校对哦~请发送“桌游查询 XXX”重新查询哦"])
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
    except:
        return [False,error, f"你说的梨花听不懂啦！是不是命令记得不清楚呀？发送“梨花命令”这四个字查看所有命令哦~"]

#查询图包信息，返回参数为图包id和图包名称
def get_tubaoname(tubao_name):

    if tubao_name.isdigit() == True :
        return get_tubaoinfo(tubao_name)

    data = []
    msg_list = []
    db_data = query(f"SELECT tubao_id,tubao_name, file_name ,display from tubao WHERE ((tubao_name like '%{tubao_name}%' or file_name like '%{tubao_name}%') and display like 'True') ")
    # 如果没有结果
    try:
        if db_data == []:
            data.append([False,error, f"图书馆里中没有搜到关于{tubao_name}的信息啦~请告诉梨花其他的名字或英文~"])
            return data
        else:
            data.append(True)
            for i in range(len(db_data)):
                msg = (
                    str(db_data[i][0])
                    + ":"
                    + db_data[i][2]
                    + "\n"
                )
                msg_list.append(msg)
            data.append(msg_list)
            return [data]
    except:
        return [False,error, f"查询失败啦！是不是命令记得不清楚呀？发送“梨花命令”这四个字查看所有命令哦~"]

#根据图包id获取图包链接
def get_tubaoinfo(tubao_id):
    data = []
    db_data = query(f"SELECT * from tubao WHERE tubao_id like '{tubao_id}' ")
    # 如果没有结果
    try:
        if db_data == []  :
            data.append([False,error, f"梨花酱没有搜到图包ID:{tubao_id}的信息呢~请发送“图包查询 XXX”重新查询哦"])
            return data
        else:
            data.append(True)
            msg = (
                "图包ID:"+ str(db_data[0][0])
                #+ "\n图包名称:"+ db_data[0][1]
                + "\n文件名称:"+ db_data[0][2]
                + "\n链接:"+ db_data[0][3]
            )
            data.append(msg)
            return [data]

    except:
        return [False,error, f"查询失败啦！是不是命令记得不清楚呀？发送“梨花命令”这四个字查看所有命令哦~"]

# -----随机图包
def randamboardgame():
    data = []
    db_data = query(f"SELECT * FROM tubao WHERE display like 'True' ORDER BY RANDOM() limit 1")

    msg = (
            "图包名称:"+ str(db_data[0][2])
            + "\n链接:"+ db_data[0][3]
        )
    data.append(msg)
    return [data]






# -----发车
def runcar(play_id,content,deadline):

    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO cheche(player_id,content,time) VALUES('{play_id}','{content}','{deadline}')"
    ) 
    #提交事务
    conn.commit()
    conn.close()
     ### -发完车的广播功能未写

# -----预约发车
def reservecar(play_id,content,deadline):

    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO reserve(player_id,content,time) VALUES('{play_id}','{content}','{deadline}')"
    ) 
    #提交事务
    conn.commit()
    conn.close()

# -----上传图包
def uploadmod(upload_id,mod_name,link):
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO tubao(tubao_name,file_name,link,upload_id,display) VALUES('{mod_name}','{mod_name}','{link}','{upload_id}','True')"
    ) 
    #提交事务
    conn.commit()
    conn.close()
     ### -发完车的广播功能未写

# -----删除（隐藏）图包
def delete_mod(mod_id):
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"UPDATE tubao SET display = 'False' WHERE tubao_id = '{mod_id}'"
    ) 
    #提交事务
    conn.commit()
    conn.close()
     ### -发完车的广播功能未写

# -----查车
def searchcar():
    data = []
    msg = []
    msg_list = []
    db_data = query(f"SELECT * from cheche ")

    try:
        if db_data == []:
            data.append([False,error, f"梨花去转了一圈，现在没有正在开的车车哦~"])
            return data
        else:
            data.append(True)
            
            for i in range(len(db_data)):
                time_str = db_data[i][3]
                time_str = time_str.replace("：", ":")
                #time_format = datetime.strptime(time_str, '%H:%M')
                now = datetime.now()
                time_now = now.strftime('%H:%M')
				
                # 20230725更新，在查车时直接查询发车人昵称
    			# 使用车车信息里的qq号进行查询
                # ====增加位置
                qqname = db_data[i][1]
                user_data = player_search_info(qqname)
                nkname=str(user_data[0][1])
				#nkname = str(user_data[0][1])
                # ====增加位置结束
                if time_str >= time_now:
                    msg = (
                    "--------------------\n【车车ID】"
                    + str(db_data[i][0])
                    + "\n【发车人】"
                    + nkname
                    +"\n"                    
                    + db_data[i][2]
                    + "\n【截止时间】"
                    + db_data[i][3]
                    + "\n--------------------"
                        )
                    msg_list.append(msg)
                elif time_str < time_now:
                    sign = False
            data.append(msg_list)
            return [data]

    except:
        return [False,error, f"查询失败啦！是不是命令记得不清楚呀？发送“梨花命令”这四个字查看所有命令哦~"]

# -----查未来车
def search_reservecar():
    data = []
    msg = []
    msg_list = []
    db_data = query(f"SELECT * from reserve ")
    try:
        if db_data == []:
            data.append([False,error, f"梨花去转了一圈，暂时没有有效的未来车车哦~"])
            return data
        else:
            data.append(True)
            for i in range(len(db_data)):
                time_str = db_data[i][3]
                time_str = time_str.replace("：", ":")
                #time_format = datetime.strptime(time_str, '%H:%M')
                now = datetime.now()
                time_now = now.strftime('%m-%d %H:%M')

                if time_str >= time_now:
                    msg = (
                    "--------------------\n车车ID："
                    + str(db_data[i][0])
                    + "\n"
                    + db_data[i][2]
                    + "\n截止时间："
                    + db_data[i][3]
                    + "\n--------------------"
                        )
                    msg_list.append(msg)
                elif time_str < time_now:
                    sign = False
            data.append(msg_list)
            return [data]

    except:
        return [False,error, f"查询失败啦！是不是命令记得不清楚呀？发送“梨花命令”这四个字查看所有命令哦~"]



# -----查询司机是否已经存在一辆车
def ifcarexist(playerid):
    data = []
    msg = []
    msg_list = []
    db_data = query(f"SELECT * from cheche ")
    try:
        if db_data == []:
            return True
        else:
            for i in range(len(db_data)):
                time_str = db_data[i][3]
                time_str = time_str.replace("：", ":")
                #time_format = datetime.strptime(time_str, '%H:%M')
                now = datetime.now()
                time_now = now.strftime('%H:%M')

                if time_str >= time_now:
                    if playerid == db_data[i][1]:
                        return False
                    else :
                        pass

                elif time_str < time_now:
                    pass


    except:
        return True


# -----封车
def delete_car(carid,playerid):
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    db_data = query(f"SELECT * from cheche ")
    if db_data == []:
        return [False,"现在车库里没有车车可以封噢"]
    
    db_data = query(f"SELECT car_id from cheche WHERE car_id ='{carid}'")
    if db_data:
        conn = sqlite3.connect(
        Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
        cur = conn.cursor()
        cur.execute(
            f"DELETE FROM cheche WHERE car_id ='{carid}'"
        )
        conn.commit()
        conn.close()
        return [True,"哥哥，强制封车成功啦！"] 
    else: 
        return [False,"车库里没有这辆车噢！"] 


# -----封车2
def delete_car2(playerid):
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cursor = cur.execute(
        f"SELECT * from cheche "
    ) 
    db_data = cur.fetchall()
    if db_data == []:
        conn.close()
        return [False,"现在车库里没有车车可以封噢"]
    cursor = cur.execute(
        f"SELECT player_id from cheche WHERE player_id = '{playerid}'"
    ) 
    db_data = cur.fetchall()
    if db_data:
        cur.execute(
            f"DELETE FROM cheche WHERE player_id = '{playerid}'"
        )
        conn.commit()
        conn.close()
        return [True,"梨花已经把你发的车封了哦~（封车功能优化，不需要输入车车ID就可以封自己的车啦！）"] 
    else: 
        conn.close()
        return [False,"你目前还没有车车噢！"] 

# -----查询图包数量
def search_mod_count():
    db_data = query(f"SELECT COUNT(*) FROM tubao")
    return db_data

# -----查询玩家数量
def search_player_count():
    db_data = query(f"SELECT COUNT(*) FROM player")
    return db_data

# -----查询图包上传者
def search_mod_uploader(mod_id):
    db_data = query(f"SELECT * from tubao WHERE tubao_id like '{mod_id}'")
    return db_data

# ---总车库记录信息
def add_garage(player_id,content,group_id,real_time):
    # 连接数据库
    conn = sqlite3.connect(
       Path(os.path.join(os.path.dirname(__file__), "resource"))/"zhuoyou.db")
    # 创建游标
    #conn = sqlite3.connect(r'D:\Github\LihuaBot\nb2\LihuaBot\src\plugins\nonebot_plugin_zhuoyouchaxun\resource\zhuoyou.db')
    cur = conn.cursor()
    cur.execute(
        f"INSERT INTO garage(player_id,content,group_id,real_time) VALUES('{player_id}','{content}','{group_id}','{real_time}')"
    ) 
    #提交事务
    conn.commit()
    conn.close()



    