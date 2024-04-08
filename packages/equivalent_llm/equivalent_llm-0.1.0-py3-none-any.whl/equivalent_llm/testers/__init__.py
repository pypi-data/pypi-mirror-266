import json
import math
from logging import Logger
from typing import Any, Callable, Optional

from langchain.output_parsers import PydanticOutputParser
from langchain.prompts import (
    ChatPromptTemplate,
    SystemMessagePromptTemplate,
    AIMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from pydantic.v1 import BaseModel, Field

class TestCounter:

    passed: int = 0
    total: int = 0

    def __iadd__(self, counter):
        self.passed += counter.passed
        self.total += counter.total
        return self

    def __add__(self, counter):
        new_counter = TestCounter()
        new_counter.passed = self.passed + counter.passed
        new_counter.total = self.total + counter.total
        return new_counter

    def count(self, validation: dict):
        self.total += 1
        if validation['passed']:
            self.passed += 1

    def fully_passed(self):
        return self.passed == self.total

    def settlement(self):
        return {'passed': self.passed, 'total': self.total}


FormatTemplate = """- format instructions: {format_instructions}"""
PreknowledgeTemplate = """- Related categories: {category}
- given information: {information}"""
EquivalenceTemplate = """- reference sentence: {reference}
- target sentence: {generated}
Question: Is target sentence equivalent to reference sentence?
"""
class EquivalenceResult(BaseModel):
    passed: bool = Field(description="Whether equivalent or not")
    score: int = Field(description="Equivalence score from 0 to 100")
    evidence: str = Field(description="The evidence of passed value")
equivalence_parser = PydanticOutputParser(pydantic_object=EquivalenceResult)

def get_equivalence_tester(definition: dict, prompt_engine: Any) -> Callable:
    # currently fixed to use ChatOpenAI
    def equivalence_tester(value: Any, reference_value: Any, instructions: list, logger: Logger) -> dict:
        try:
            system_template = SystemMessagePromptTemplate.from_template(FormatTemplate)
            ai_template = AIMessagePromptTemplate.from_template(PreknowledgeTemplate)
            human_template = HumanMessagePromptTemplate.from_template(EquivalenceTemplate)
            prompt_template = ChatPromptTemplate.from_messages(
                [system_template, ai_template, human_template]
            )
            final_prompt = prompt_template.format_prompt(
                reference=reference_value,
                generated=value,
                category=definition['category'],
                information=instructions if instructions is not None else "No information",
                format_instructions=equivalence_parser.get_format_instructions(),
            ).to_messages()
            logger.debug(f"Equivalence Prompt: {final_prompt}")
            result = prompt_engine(final_prompt)

            # markdown json format
            if result.content.startswith("```json"):
                return json.loads(result.content.split("```json")[1].split("```")[0])
            else:
                return json.loads(result.content)
        except Exception as e:
            logger.debug(f"Equvalence Error: {e}")
            return {
                'passed': False,
                'level': 'fatal',
                'evidence': {
                    'type': 'validation process',
                    'message': str(e),
                }
            }
    return equivalence_tester

# consistency testers

LatestRequestedTemplate = """- Given information: {given_information}"""
NumberConsistencyTemplate = """- Answer a question by true or false of passed with concrete evidence.
- Question: Is below a value is consistently matched with given information? {range_sentence}
{comment}
- target value: {generated}
"""

def get_number_consistency_tester(definition: dict, prompt_engine: Any) -> Callable:
    def number_tester(value: Any, reference_value: Any, instructions: list, logger: Logger) -> dict:
        range_sentence = ''
        if definition.get('range') is not None:
            if definition['range'][0] == -math.inf:
                range_sentence = f"Also, is the value less or equal than {definition['range'][1]}?"
            elif definition['range'][1] == math.inf:
                range_sentence = f"Also, is the value greater or equal than {definition['range'][0]}?"
            else:
                range_sentence = f"Also, is the value between {definition['range'][0]} and {definition['range'][1]}?"
        logger.debug(f"Range sentence: {range_sentence}")
        try:
            system_template = SystemMessagePromptTemplate.from_template(FormatTemplate)
            ai_template = AIMessagePromptTemplate.from_template(LatestRequestedTemplate)
            human_template = HumanMessagePromptTemplate.from_template(NumberConsistencyTemplate)
            prompt_template = ChatPromptTemplate.from_messages(
                [system_template, ai_template, human_template]
            )
            final_prompt = prompt_template.format_prompt(
                generated=value,
                given_information=instructions if instructions is not None else "No information",
                range_sentence=range_sentence,
                comment=definition.get('comment', ''),
                format_instructions=equivalence_parser.get_format_instructions(),
            ).to_messages()
            logger.debug(f"Number Consistency Prompt: {final_prompt}")
            result = prompt_engine(final_prompt)

            # markdown json format
            if result.content.startswith("```json"):
                return json.loads(result.content.split("```json")[1].split("```")[0])
            else:
                return json.loads(result.content)
        except Exception as e:
            logger.debug(f"Number Consistency Error: {e}")
            return {
                'passed': False,
                'level': 'fatal',
                'evidence': {
                    'type': 'validation process',
                    'message': str(e),
                }
            }
    return number_tester

CategoryConsistencyTemplate = """- Answer a question by true or false of passed with concrete evidence.
- Question: Is below phrase is matched with given information of following categories: {category_sentence}?
  {comment}
- target sentence: {generated}
"""

def get_category_consistency_tester(definition: dict, prompt_engine: Any) -> Callable:
    def category_tester(value: Any, reference_value: Any, instructions: list, logger: Logger) -> dict:
        try:
            system_template = SystemMessagePromptTemplate.from_template(FormatTemplate)
            ai_template = AIMessagePromptTemplate.from_template(LatestRequestedTemplate)
            human_template = HumanMessagePromptTemplate.from_template(CategoryConsistencyTemplate)
            prompt_template = ChatPromptTemplate.from_messages(
                [system_template, ai_template, human_template]
            )
            final_prompt = prompt_template.format_prompt(
                generated=value,
                given_information=instructions if instructions is not None else "No information",
                category_sentence=definition['category'],
                comment=definition.get('comment', ''),
                format_instructions=equivalence_parser.get_format_instructions(),
            ).to_messages()
            logger.debug(f"Category Consistency Prompt: {final_prompt}")
            result = prompt_engine(final_prompt)
            # markdown json format
            if result.content.startswith("```json"):
                return json.loads(result.content.split("```json")[1].split("```")[0])
            else:
                return json.loads(result.content)
        except Exception as e:
            logger.debug(f"Category Consistency Error: {e}")
            return {
                'passed': value == reference_value,
                'evidence': {
                    'type': 'validation process',
                    'message': str(e),
                }
            }
    return category_tester

EnumConsistencyTemplate = """- Answer a question by true or false of passed with concrete evidence.
- Question: Is below phrase is matched with given enum items: {enum_items}?
  {comment}
- target sentence: {generated}
"""

def get_enum_consistency_tester(definition: dict, prompt_engine: Any) -> Callable:
    def enum_tester(value: Any, reference_value: Any, instructions: list, logger: Logger) -> dict:
        try:
            system_template = SystemMessagePromptTemplate.from_template(FormatTemplate)
            ai_template = AIMessagePromptTemplate.from_template(LatestRequestedTemplate)
            human_template = HumanMessagePromptTemplate.from_template(EnumConsistencyTemplate)
            prompt_template = ChatPromptTemplate.from_messages(
                [system_template, ai_template, human_template]
            )
            final_prompt = prompt_template.format_prompt(
                generated=value,
                given_information=instructions if instructions is not None else "No information",
                enum_items=definition['itmes'],
                comment=definition.get('comment', ''),
                format_instructions=equivalence_parser.get_format_instructions(),
            ).to_messages()
            logger.debug(f"Enum Consistency Prompt: {final_prompt}")
            result = prompt_engine(final_prompt)
            # markdown json format
            if result.content.startswith("```json"):
                return json.loads(result.content.split("```json")[1].split("```")[0])
            else:
                return json.loads(result.content)
        except Exception as e:
            logger.debug(f"Enum Consistency Error: {e}")
            return {
                'passed': value == reference_value,
                'evidence': {
                    'type': 'validation process',
                    'message': str(e),
                }
            }
    return enum_tester

GrammarTemplate = """- You are a experienced grammarian.
- Answer a question by true or false of passed with concrete evidence.
- Question: Is below sentence is composed with STRICTLY correct grammar for Korean, English, or mixture of Korean and English, is it acceptable to read naturally?
  If sentence is just a word, it is considered as correct.
  {comment}
- target sentence: {generated}
"""

def get_grammar_tester(definition: dict, prompt_engine: Any) -> Callable:
    def grammar_tester(value: Any, reference_value: Any, instructions: Optional[list], logger: Logger) -> dict:
        try:
            system_template = SystemMessagePromptTemplate.from_template(FormatTemplate)
            human_template = HumanMessagePromptTemplate.from_template(GrammarTemplate)
            prompt_template = ChatPromptTemplate.from_messages(
                [system_template, human_template]
            )
            final_prompt = prompt_template.format_prompt(
                generated=value,
                comment=definition.get('comment', ''),
                format_instructions=equivalence_parser.get_format_instructions(),
            ).to_messages()
            logger.debug(f"Grammar Prompt: {final_prompt}")
            result = prompt_engine(final_prompt)

            # markdown json format
            if result.content.startswith("```json"):
                return json.loads(result.content.split("```json")[1].split("```")[0])
            else:
                return json.loads(result.content)
        except Exception as e:
            logger.debug(f"Grammar Error: {e}")
            return {
                'passed': value == reference_value,
                'evidence': {
                    'type': 'validation process',
                    'message': str(e),
                }
            }
    return grammar_tester

class EleganceResult(BaseModel):
    passed: bool = Field(description="Whether equivalent or not")
    score: int = Field(description="Equivalence score from 0 to 100")
    evidence: str = Field(description="The evidence of passed value")
    alternative: str = Field(description="Alternative sentence")
elegance_parser = PydanticOutputParser(pydantic_object=EleganceResult)

PreknowledgeTemplate = """- given information: {information}"""
EleganceTemplate = """- reference sentence: {reference}
- Question: Is below target sentence centainly superior elegant than, reference sentence?
  Please provide a elegant and human readable alternative as well by orignial language of target sentence with same tone.
  {comment}
- target sentence: {generated}
"""

"Is the sentence below equivalent to, or even more elegant than, the standard sentence? Please provide a fluid and refined alternative as well."
def get_elegance_tester(definition: dict, prompt_engine: Any) -> Callable:
    # currently fixed to use ChatOpenAI
    def elegance_tester(value: Any, reference_value: Any, instructions: list, logger: Logger) -> dict:
        try:
            system_template = SystemMessagePromptTemplate.from_template(FormatTemplate)
            ai_template = AIMessagePromptTemplate.from_template(PreknowledgeTemplate)
            human_template = HumanMessagePromptTemplate.from_template(EleganceTemplate)
            prompt_template = ChatPromptTemplate.from_messages(
                [system_template, ai_template, human_template]
            )
            final_prompt = prompt_template.format_prompt(
                reference=reference_value,
                generated=value,
                comment=definition.get('comment', ''),
                information=instructions if instructions is not None else "No information",
                format_instructions=elegance_parser.get_format_instructions(),
            ).to_messages()
            logger.debug(f"Elegance Prompt: {final_prompt}")
            result = prompt_engine(final_prompt)

            # markdown json format
            if result.content.startswith("```json"):
                return json.loads(result.content.split("```json")[1].split("```")[0])
            else:
                return json.loads(result.content)
        except Exception as e:
            logger.debug(f"Elegance Error: {e}")
            return {
                'passed': False,
                'level': 'fatal',
                'evidence': {
                    'type': 'validation process',
                    'message': str(e),
                }
            }
    return elegance_tester
