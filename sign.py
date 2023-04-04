import os
import json
import random
from datetime import datetime

from nonebot.adapters import Bot, Event


# 签到积分范围
SIGN_SCORE_RANGE = (1, 10)
# JSON 文件路径
JSON_FILE_PATH = 'data/sign.json'
# 签到数据
sign_data = {}

# 检查 JSON 文件是否存在，如果不存在则新建一个空的 JSON 文件
if not os.path.exists(JSON_FILE_PATH):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump({}, f)


# 读取签到数据的函数
def load_sign_data():
    with open(JSON_FILE_PATH, 'r', encoding='utf-8') as f:
        return json.load(f)


# 保存签到数据的函数
def save_sign_data(data):
    with open(JSON_FILE_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f)


# 获取今天的日期字符串，格式为 yyyy-mm-dd
def get_today():
    return datetime.now().strftime('%!!(MISSING)!(MISSING)Y(MISSING)-%!!(MISSING)!(MISSING)m(MISSING)-%!!(MISSING)!(MISSING)d(MISSING)')


# 处理签到指令的函数
async def sign(bot: Bot, event: Event):
    # 获取用户 ID
    user_id = event.get('user_id')
    # 获取签到数据
    global sign_data
    sign_data = load_sign_data()
    # 获取今天的日期
    today = get_today()

    # 如果今天已经签到过了，返回已经签到过的消息
    if user_id in sign_data.get(today, []):
        return await bot.send(event, '您今天已经签到过了')

    # 随机增加金币
    score = random.randint(*SIGN_SCORE_RANGE)
    # 更新签到数据
    if today not in sign_data:
        sign_data[today] = []
    sign_data[today].append((user_id, score))
    # 更新用户金币数量
    if user_id not in sign_data['users']:
        sign_data['users'][user_id] = 0
    sign_data['users'][user_id] += score
    # 保存签到数据
    save_sign_data(sign_data)

    # 返回签到成功的消息
    return await bot.send(event, f'签到成功！获得了 {score} 个金币')


# 处理查询金币数量的指令的函数
async def score(bot: Bot, event: Event):
    # 获取用户 ID
    user_id = event.get('user_id')
    # 获取签到数据
    global sign_data
    sign_data = load_sign_data()
    # 获取用户金币数量
    score = sign_data['users'].get(str(user_id), 0)
    # 返回用户金币数量
    return await bot.send(event, f'您当前的金币数量为 {score} 个')


# 在启动时加载签到数据
sign_data = load_sign_data()