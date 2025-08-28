

from fastapi import APIRouter
from fastapi.concurrency import run_in_threadpool

from controller.personal_controller import (get_personal_info_controller,
                                            personal_translator_controller)
from schemas import PersonalInfo

personal_routes:APIRouter=APIRouter()

@personal_routes.get("/")
async def get_personal_info_router():
   return await run_in_threadpool(get_personal_info_controller)

@personal_routes.post('/translate')
async def personal_translator_router(personal_data:PersonalInfo):
    return await run_in_threadpool(personal_translator_controller, personal_data)
