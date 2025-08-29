
from sqlalchemy.orm import Session

from schemas import PersonalInfo
from services import get_personal_info_service, personal_translate_service


def get_personal_info_controller(language:str,db:Session):
    return  get_personal_info_service(language,db)

def personal_translator_controller(personal_data:PersonalInfo,db:Session):
    return personal_translate_service(personal_data,db)
