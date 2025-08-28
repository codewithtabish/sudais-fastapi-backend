import json
from typing import List

from fastapi.responses import JSONResponse
from langchain_core.output_parsers import StrOutputParser
from langchain_core.prompts import PromptTemplate
from langchain_openai import ChatOpenAI
from openai import OpenAIError
from pydantic import ValidationError

from constants import languages
from schemas import PersonalInfo, PersonalTranslationResponse, Translation


def get_personal_info_service() -> PersonalInfo:
    return PersonalInfo(
        name='zain khan',
        short_info='Android, React Native & backend developer. Passionate about building and automating modern solutions. ...',
        local='English'
    )


def personal_translate_service(personal_data: PersonalInfo) -> PersonalTranslationResponse:
    try:
        llm = ChatOpenAI()
        translations_list: List[Translation] = []

        for lang_code in languages:
            # Template to translate name + short_info fully
            translator_template = PromptTemplate(
                template=f"""
You are a professional translator. Translate the following fully into {lang_code}, including greetings and names:

Text to translate:
- Name: {{name}}
- Short Info: {{short_info}}

Return the output as a JSON object with keys "name" and "short_info".
Ensure proper translation or transliteration for names and greeting text.
""",
                input_variables=['name', 'short_info']
            )

            # Build chain
            chain = translator_template | llm | StrOutputParser()

            # Call LLM
            try:
                response_str = chain.invoke({
                    'name': personal_data.name,
                    'short_info': personal_data.short_info
                })
            except OpenAIError as e:
                # Handle OpenAI exceptions
                response_str = json.dumps({
                    'name': personal_data.name,
                    'short_info': personal_data.short_info
                })

            # Convert LLM output to dict safely
            try:
                response_dict = json.loads(response_str)
            except Exception:
                response_dict = {
                    'name': personal_data.name,
                    'short_info': personal_data.short_info
                }

            # Append each translation as a Pydantic model
            translations_list.append(Translation(
                language=lang_code,
                name=response_dict.get('name', personal_data.name),
                short_info=response_dict.get('short_info', personal_data.short_info)
            ))

        # Wrap in response model with status_code and message
        response_model = PersonalTranslationResponse(
            status_code=200,
            message="Translations fetched successfully",
            traslated_into=len(translations_list),
            translations=translations_list
        )
        return response_model

    except ValidationError as e:
        error_messages = [
            f"{'.'.join([str(loc) for loc in err['loc']])}: {err['msg']}" 
            for err in e.errors()
        ]
        return PersonalTranslationResponse(
            status_code=400,
            message="Invalid input",
            translations=[]
        )

    except AttributeError as e:
        return PersonalTranslationResponse(
            status_code=400,
            message=f"Missing field in input: {str(e)}",
            translations=[]
        )

    except OpenAIError as e:
        return PersonalTranslationResponse(
            status_code=502,
            message=f"OpenAI API error: {str(e)}",
            translations=[]
        )

    except Exception as e:
        return PersonalTranslationResponse(
            status_code=500,
            message=f"Internal server error: {str(e)}",
            translations=[]
        )
