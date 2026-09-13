from datetime import datetime

from sqlalchemy import select, func, delete
from sqlalchemy.ext.asyncio import AsyncSession
from models.history import History
from models.news import News


async def add_history(
        db:AsyncSession,
        user_id:int,
        news_id:int
):
    query = select(History).where(History.user_id == user_id, History.news_id == news_id)
    result = await db.execute(query)
    existing_history = result.scalar_one_or_none()
    if existing_history:
        existing_history.view_time = datetime.now()
        await db.commit()
        await db.refresh(existing_history)
        return existing_history
    else:
        history=History(user_id=user_id,news_id=news_id)
        db.add(history)
        await db.commit()
        await db.refresh(history)
        return history

async def get_history_list(
        page:int,
        page_size:int,
        db:AsyncSession,
        user_id:int
):
    count=select(func.count()).select_from(History).where(History.user_id==user_id)
    result=await db.execute(count)
    total=result.scalar_one_or_none()

    offset= (page-1)*page_size
    query=(select(News,History.view_time.label("view_time"))
            .join(History,History.news_id==News.id)
            .where(History.user_id==user_id)
            .order_by(History.view_time.desc())
            .offset(offset).limit(page_size))
    result=await db.execute(query)
    rows=result.all()
    return total,rows


async def remove_history(
        db:AsyncSession,
        user_id:int,
        news_id:int,
):
    text=delete(History).where(History.user_id==user_id,History.news_id==news_id)
    result=await db.execute(text)
    return result.rowcount>0


async def remove_all_history(
        user_id:int,
        db:AsyncSession
):
    stmt=delete(History).where(History.user_id==user_id)
    result=await db.execute(stmt)
    await db.commit()
    return result.rowcount or 0