from fastapi import APIRouter, Depends, Query, HTTPException
from fastapi.params import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette import status

from config.db_conf import get_db
from crud import history
from crud.history import remove_all_history
from models.users import User
from schemas.history import HistoryAddRequest, HistoryListResponse
from utils.auth import get_current_user
from utils.response import success_response

router=APIRouter(prefix="/api/history",tags=["history"])

@router.post("/add")
async def add_history(
        data:HistoryAddRequest,
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user)
):
    result=await history.add_history(db,user.id,data.news_id)
    return success_response(message="添加成功",data=result)

@router.get("/list")
async def get_history_list(
        page:int=Query(1,ge=1),
        page_size:int=Query(10,ge=1,le=100,alias="pageSize"),
        db:AsyncSession=Depends(get_db),
        user:User=Depends(get_current_user)
):
    total,rows=await history.get_history_list(page,page_size,db,user.id)
    history_list=[{
        **news.__dict__,
        "viewTime":viewTime
    }for news,viewTime in rows]

    has_more=total>(page-1)*page_size

    data=HistoryListResponse(list=history_list,total=total,hasMore=has_more)
    return success_response(message="success",data=data)

@router.delete("/delete/{history_id}")
async def remove_history(
        history_id:int,
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    result=await history.remove_history(db,user.id,history_id)
    if not result:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="收藏记录不存在")
    return success_response(message="删除成功")

@router.delete("/clear")
async def clear_history(
        user:User=Depends(get_current_user),
        db:AsyncSession=Depends(get_db)
):
    result=await remove_all_history(user.id,db)
    return success_response(message="清空成功")














