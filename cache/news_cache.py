# 新闻相关的缓存方式:新闻分类的读取和写入
# key-value
from typing import List, Dict, Any, Optional
from config.cache_conf import get_json_cache, set_cache

CATEGORIES_KEY="news:categories"
NEWS_LIST_PREFIX="news_list:"
NEWS_DETAIL_PREFIX="news_detail:"
NEWS_RELATED_PREFIX="news_related:"


# 获取新闻分类缓存
async def get_cached_categories():
    return await get_json_cache(CATEGORIES_KEY)

# 写入新闻分类缓存：缓存的数据，过期时间
# 分类、配置 7200  列表：600  详情：1800  验证码：120  --数据越稳定，缓存越持久
async def set_cache_categories(data:List[Dict[str,Any]],expire:int=7200):
    return await set_cache(CATEGORIES_KEY,data,expire)

# 写入缓存-新闻列表 key=news_list:分类id:页码:每页数量 + 列表数据 + 过期时间
async def set_cache_news_list(category_id:Optional[int],page:int,size:int,news_list:List[Dict[str,Any]],expire=600):
    # 调用 封装的 Redis 的设置方法，存新闻列表到缓存
    category_part=category_id if category_id is not None else "all"
    key=f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await set_cache(key,news_list,expire)

# 读取缓存-新闻列表
async def get_cache_news_list(category_id:Optional[int],page:int,size:int):
    category_part = category_id if category_id is not None else "all"
    key = f"{NEWS_LIST_PREFIX}{category_part}:{page}:{size}"
    return await get_json_cache(key)


# 写入缓存-新闻详情  key = news_detail:新闻id
async def set_cache_news_detail(news_id:int,data:Dict[str,Any]):
    key=f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await set_cache(key,data,expire=600)


# 读取缓存-新闻详情
async def get_cache_news_detail(news_id:int):
    key = f"{NEWS_DETAIL_PREFIX}{news_id}"
    return await get_json_cache(key)



# 写入缓存-推荐新闻 key=news_related:新闻id:分类id
async def set_cache_news_related(news_id:int,news_category_id:int,data:List[Dict[str,Any]]):
    key=f"{NEWS_RELATED_PREFIX}{news_id}:{news_category_id}"
    return await set_cache(key,data)

# 读取缓存-推荐新闻
async def get_cache_news_related(news_id:int,news_category_id):
    key=f"{NEWS_RELATED_PREFIX}{news_id}:{news_category_id}"
    return await get_json_cache(key)




















