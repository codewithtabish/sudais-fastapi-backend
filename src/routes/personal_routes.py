

from fastapi import APIRouter, Depends
from fastapi.concurrency import run_in_threadpool
from sqlalchemy.orm import Session

from controller.personal_controller import (
    get_personal_info_controller,
    personal_translator_controller,
)
from db.dependencies import get_db
from schemas import PersonalInfo

personal_routes:APIRouter=APIRouter()

@personal_routes.get("/{language}")
async def get_personal_info_router(db:Session=Depends(get_db),language:str='English'):
   return await run_in_threadpool(get_personal_info_controller,language,db)

@personal_routes.post('/translate')
async def personal_translator_router(personal_data:PersonalInfo,db:Session=Depends(get_db)):
    return await run_in_threadpool(personal_translator_controller, personal_data, db)
