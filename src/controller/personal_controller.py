
from schemas import PersonalInfo
from services import get_personal_info_service, personal_translate_service


def get_personal_info_controller():
    return  get_personal_info_service()

def personal_translator_controller(personal_data:PersonalInfo):
    return personal_translate_service(personal_data)
