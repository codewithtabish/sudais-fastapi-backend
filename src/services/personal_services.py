import json
from datetime import datetime
from typing import List

from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAIError
from pydantic import ValidationError
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import Session

from constants import language_codes, languages
from models import PersonalInfoModel, PersonalInfoTranslationModel
from schemas import PersonalInfo, PersonalTranslationResponse, Translation

# Create mapping dictionaries
name_to_code = dict(zip(languages, language_codes))
code_to_name = dict(zip(language_codes, languages))


def get_personal_info_service(language: str, db: Session):
    try:
        # Normalize input: allow both full name or code
        language_lower = language.lower()
        normalized_language = code_to_name.get(language_lower) or next(
            (l for l in languages if l.lower() == language_lower), None
        )

        if not normalized_language:
            return jsonable_encoder({
                "status_code": 400,
                "message": f"Unsupported language '{language}'",
                "data": None
            })

        # Query only the requested language translation
        result = (
            db.query(PersonalInfoModel, PersonalInfoTranslationModel)
            .join(PersonalInfoTranslationModel, PersonalInfoModel.id == PersonalInfoTranslationModel.personal_info_id)
            .filter(PersonalInfoTranslationModel.language == normalized_language)
            .first()
        )

        if not result:
            return jsonable_encoder({
                "status_code": 404,
                "message": f"No personal info found for language '{normalized_language}'",
                "data": None
            })

        personal_info_model, translation = result

        # Build JSON response
        response = {
            "id": personal_info_model.id,
            "slug": personal_info_model.slug,
            "created_at": personal_info_model.created_at,
            "updated_at": personal_info_model.updated_at,
            "translation": {
                "language": translation.language,
                "name": translation.name,
                "short_info": translation.short_info,
                "image_url": translation.image_url,
            },
        }

        return jsonable_encoder({
            "status_code": 200,
            "message": f"Personal info fetched successfully for '{normalized_language}'",
            "data": response
        })

    except SQLAlchemyError as e:
        # Handle database-related errors
        return jsonable_encoder({
            "status_code": 500,
            "message": f"Database error: {str(e)}",
            "data": None
        })
    except Exception as e:
        # Handle any other unexpected errors (network issues, runtime errors)
        return jsonable_encoder({
            "status_code": 500,
            "message": f"Internal server error: {str(e)}",
            "data": None
        })
def personal_translate_service(personal_data: PersonalInfo, db: Session) -> PersonalTranslationResponse:
    try:
        llm = ChatOpenAI()
        translations_list: List[Translation] = []

        # Generate slug from name
        slug = personal_data.name.lower().replace(" ", "-")

        # Check if record exists
        personal_info_db = db.query(PersonalInfoModel).filter_by(slug=slug).first()

        if personal_info_db:
            # Update existing record
            personal_info_db.slug = slug
            personal_info_db.updated_at = datetime.utcnow()
        else:
            # Create new record
            personal_info_db = PersonalInfoModel(
                slug=slug,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow(),
            )
            db.add(personal_info_db)
            db.flush()  # assign ID before using it

        # Process translations
        for lang_code in languages:
            translator_template = PromptTemplate(
                template=f"""
You are a professional translator. Translate the following text into {lang_code}.
Do NOT add any labels like "Name:" or "Short Info:". Only return the raw translated content.

Text to translate:
Name = {{name}}
Short Info = {{short_info}}

Return JSON strictly in this format:
{{{{ 
  "name": "translated name", 
  "short_info": "translated short info" 
}}}}
""",
                input_variables=["name", "short_info"],
            )

            chain = translator_template | llm | StrOutputParser()

            try:
                response_str = chain.invoke(
                    {
                        "name": personal_data.name,
                        "short_info": personal_data.short_info,
                    }
                )
            except OpenAIError:
                response_str = json.dumps(
                    {
                        "name": personal_data.name,
                        "short_info": personal_data.short_info,
                    }
                )

            # Parse safely
            try:
                response_dict = json.loads(response_str)
            except Exception:
                response_dict = {
                    "name": personal_data.name,
                    "short_info": personal_data.short_info,
                }

            # Check if translation for this language already exists
            translation_db = (
                db.query(PersonalInfoTranslationModel)
                .filter_by(language=lang_code, personal_info_id=personal_info_db.id)
                .first()
            )

            if translation_db:
                # Update existing translation
                translation_db.name = response_dict.get("name", personal_data.name)
                translation_db.short_info = response_dict.get("short_info", personal_data.short_info)
                translation_db.image_url = personal_data.image_url
                translation_db.updated_at = datetime.utcnow()
            else:
                # Create new translation
                translation_db = PersonalInfoTranslationModel(
                    language=lang_code,
                    name=response_dict.get("name", personal_data.name),
                    short_info=response_dict.get("short_info", personal_data.short_info),
                    image_url=personal_data.image_url,
                    personal_info_id=personal_info_db.id,
                )
                db.add(translation_db)

            # Add to response
            translations_list.append(
                Translation(
                    language=lang_code,
                    name=response_dict.get("name", personal_data.name),
                    short_info=response_dict.get("short_info", personal_data.short_info),
                    image_url=personal_data.image_url,
                )
            )

        # Commit everything once
        db.commit()
        db.refresh(personal_info_db)

        return PersonalTranslationResponse(
            status_code=200,
            message="Translations fetched successfully",
            traslated_into=len(translations_list),
            translations=translations_list,
        )

    except ValidationError:
        return PersonalTranslationResponse(
            status_code=400, message="Invalid input", traslated_into=0, translations=[]
        )

    except AttributeError as e:
        return PersonalTranslationResponse(
            status_code=400,
            message=f"Missing field in input: {str(e)}",
            traslated_into=0,
            translations=[],
        )

    except OpenAIError as e:
        return PersonalTranslationResponse(
            status_code=502,
            message=f"OpenAI API error: {str(e)}",
            traslated_into=0,
            translations=[],
        )

    except Exception as e:
        return PersonalTranslationResponse(
            status_code=500,
            message=f"Internal server error: {str(e)}",
            traslated_into=0,
            translations=[],
        )
