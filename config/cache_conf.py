import os
import json
from typing import Any
import redis.asyncio as redis
from dotenv import load_dotenv

load_dotenv()

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.from_url(REDIS_URL, decode_responses=True)

# 设置 和 读取（字符串 和 列表和字典） “[{}]”
# 读取： 字符串
async def get_cache(key:str):
    try:
        return await redis_client.get(key)
    except Exception as e:
        print(f"获取缓存失败：{e}")
        return None

# 读取： 列表或者字典
async def get_json_cache(key:str):
    try:
        data=await redis_client.get(key)
        if data:
            return json.loads(data)
        return None
    except Exception as e:
        print(f"获取 JSON 缓存失败：{e}")
        return None

# 设置缓存 setex(key,expire,value)
async def set_cache(key:str,value:Any,expire:int=3600):
    try:
        if isinstance(value,(dict,list)):
            # 转字符串再存
            value=json.dumps(value,ensure_ascii=False) # 中文正常保存
        await redis_client.setex(key,expire,value)
        return True
    except Exception as e:
        print(f"设置缓存失败：{e}")
        return False





















