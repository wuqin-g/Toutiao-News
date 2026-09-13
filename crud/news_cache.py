from fastapi.encoders import jsonable_encoder
from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import update

from cache.news_cache import get_cached_categories, set_cache_categories, get_cache_news_list, set_cache_news_list, \
    get_cache_news_detail, set_cache_news_detail, get_cache_news_related, set_cache_news_related
from models.news import Category,News
from schemas.base import NewsItemBase


async def get_categories(db:AsyncSession,skip:int =0,limit:int=100):
    # 先尝试从缓存中获取数据
    cached_categories= await get_cached_categories()
    if cached_categories:
        return cached_categories

    stmt=select(Category).offset(skip).limit(limit)
    result=await db.execute(stmt)
    categories=result.scalars().all()

    # 写入缓存
    if categories:
        categories=jsonable_encoder(categories)
        await set_cache_categories(categories)

    return categories

async def get_news_list(db:AsyncSession,category_id:int,skip:int=0,limit:int=10):
    # 先尝试从缓存获取新闻列表
    # 跳过的数量 页码=跳过数量//每页数量 + 1
    # await get_cache_news_list(分类id,页码,每页数量)
    page=skip//limit + 1
    cached_list=await get_cache_news_list(category_id,page,limit) # 缓存json
    if cached_list :
        return [News(**item) for item in cached_list]

    # 查询的是指定分类下的所以新闻
    stmt=select(News).where(News.category_id==category_id).offset(skip).limit(limit)
    result=await db.execute(stmt)
    news_list= result.scalars().all()

    # 写入缓存
    if news_list:
        # 先把 ORM 数据 转换 字典才能写入缓存
        # ORM 转成 pydantic,再转成 字典
        # by_alias=False 不适用别名，保存python 风格，因为Redis 数据是给后段用的
        news_data=[NewsItemBase.model_validate(item).model_dump(mode="json",by_alias=False)for item in news_list]
        await  set_cache_news_list(category_id,page,limit,news_data)
    return news_list


async def get_news_count(db:AsyncSession,category_id:int):

    stmt = select(func.count(News.id)).where(News.category_id==category_id)
    result = await db.execute(stmt)
    return result.scalar_one()  # 只能有一个结果，否则报错

async def get_news_detail(db:AsyncSession,news_id:int):
    # 先尝试从缓存中获取新闻详情
    cached_detail=await get_cache_news_detail(news_id)
    if cached_detail:
        return News(**cached_detail)

    stmt=select(News).where(News.id==news_id)
    result=await db.execute(stmt)
    news_detail= result.scalar_one_or_none()

    # 写入缓存
    if news_detail:
        news_dict = NewsItemBase.model_validate(news_detail).model_dump(
            mode="json",
            by_alias=False
        )
        await set_cache_news_detail(news_id,news_dict)

    return news_detail


async def increase_news_views(db:AsyncSession,news_id:int):
    stmt=update(News).where(News.id==news_id).values(views=News.views+1)
    result=await db.execute(stmt)
    await db.commit()

    # 更新 -》检查数据库是否真的命中了数据 -》 命中了返回True
    return result.rowcount>0

async def get_related_news(db:AsyncSession,news_id:int,category_id:int,limit:int=5):
    # 尝试从缓存获取推荐新闻
    cached_related=await get_cache_news_related(news_id,category_id)
    if cached_related:
        return cached_related

    stmt=select(News).where(
        News.category_id == category_id,
        News.id != news_id
    ).order_by(
        News.views.desc(),
        News.publish_time.desc()
    ).limit(limit)
    result=await db.execute(stmt)
    related_news=result.scalars().all()
    # 列表推导式
    related_list=[{"id":news_detail.id,
            "title":news_detail.title,
            "content":news_detail.content,
            "image":news_detail.image,
            "author":news_detail.author,
            "publishTime":news_detail.publish_time.isoformat(),
            "categoryId":news_detail.category_id,
            "views":news_detail.views,
    }for news_detail in related_news]

    # 写入缓存
    if related_list:
        await set_cache_news_related(news_id,category_id,related_list)
    return related_list












