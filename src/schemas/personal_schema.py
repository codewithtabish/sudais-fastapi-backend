from typing import List, Literal, Optional

from pydantic import BaseModel, Field, field_validator

from constants import languages

# Instead of Literal[*languages], we can do this for Python <3.12 compatibility:

class PersonalInfo(BaseModel):
    name: str = Field(default='Hey This is me SUDAIS AZLAN')
    short_info: str = Field(
        default='Android, React Native & backend developer. Passionate about building and automating modern solutions. ...'
    )
    local: str = Field(default='English', description='language code')

    @field_validator('local')
    def check_language_exists(cls, passed_language):
        if passed_language not in languages:
            raise ValueError(f"Language '{passed_language}' is not supported")
        return passed_language

# Model for single translation
class Translation(BaseModel):
    language: str  # use str instead of Literal if Literal[*languages] fails
    name: str
    short_info: str

# Model for full response
class PersonalTranslationResponse(BaseModel):
    status_code: int = Field(default=200, description="HTTP status code of the response")
    message: str = Field(default="Translations fetched successfully")
    traslated_into:Optional[int]=Field(default=0,description="Number of languages translated into")
    # Field(default=0,description="Number of languages translated into")
    translations: List[Translation]
