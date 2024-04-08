import json
from logging import Logger

from langchain.prompts import ChatPromptTemplate, SystemMessagePromptTemplate, HumanMessagePromptTemplate
from langchain.output_parsers import PydanticOutputParser
from langchain_openai import ChatOpenAI

from pydantic.v1 import BaseModel, Field

__system_template = '''
- format instructions: {format_instructions}
- When you reserve a movie at movie theater, you should think following considerations.
- DATETIME: time, data, and datetime
- LOCATION': district, place name, landmark, and company name near by theater, and so on. MUST NOT include theater name.
- COORDINATES: coordinates by longitude and latitude
- THEATER': theater name
- ACTOR: well-known actor or actress names
- MOVIE_GENRE: movie genre, which also includes special circumstance like "date" and "relaxation"
- MOVIE_TITLE: specific movie title. Generic name like "영화" MUST NOT belong in this element.
- DECISION: acception or rejection in English or Korean
- RESERVATION: reservation, booking, or cancelation
'''

__human_template = '''
- What kinds of elements are contained below message? Choose the element type at first and describe the evidence of decision.
- MUST exclude elements out of instruction
- MESSAGE: {message}
'''

class UserEntity(BaseModel):
    entity: str = Field(desription="Entity type in user input message")
    keyword: str = Field(description="Core keyword of entity")
    evidence: str = Field(description="Evidence of decision")

class ListOfUserEntity(BaseModel):
    entities: list[UserEntity] = Field(description="List of entities")

def get_entities(message: str, instructions: list, prompt_engine: ChatOpenAI, logger: Logger) -> dict:
    system_template = SystemMessagePromptTemplate.from_template(__system_template)
    human_template = HumanMessagePromptTemplate.from_template(__human_template)
    chat_prompt_template = ChatPromptTemplate.from_messages(
        [system_template, human_template]
    )

    parser = PydanticOutputParser(pydantic_object=ListOfUserEntity)
    final_prompt = chat_prompt_template.format_prompt(
        message=message,
        format_instructions=parser.get_format_instructions()
    ).to_messages()
    logger.debug(f"Prompt for user input message: {final_prompt}")

    result = prompt_engine(final_prompt)
    parsed = json.loads(result.content.split("```json")[1].split("```")[0])
    parsed['role'] = 'user'
    parsed['name'] = 'user'
    parsed['request'] = message
    return parsed
