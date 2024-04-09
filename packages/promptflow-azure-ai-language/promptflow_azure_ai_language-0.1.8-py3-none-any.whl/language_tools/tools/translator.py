# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import uuid
from promptflow import tool
from promptflow.connections import CustomConnection
from language_utils.language_skill import LanguageSkill
from language_utils.language_tool_utils import run_language_skill

API_VERSION = "3.0"
SKILL = LanguageSkill.TRANSLATION


@tool
def get_translation(connection: CustomConnection,
                    text: str,
                    translate_to: list,
                    source_language: str = "",
                    category: str = "general",
                    text_type: str = "plain",
                    max_retries: int = 5,
                    max_wait: int = 60,
                    parse_response: bool = False):
    # Create input:
    input = {"Text": text}

    # Create query parameters:
    query_parameters = {
        "api-version": API_VERSION,
        "ClientTraceId": str(uuid.uuid4()),
        "to": ",".join(translate_to),
        "category": category,
        "textType": text_type
    }
    if len(source_language) != 0:
        query_parameters["from"] = source_language

    # Create task parameters:
    task_parameters = {}

    # Create skill config:
    skill_config = {
        "connection": connection,
        "query_parameters": query_parameters,
        "input": input,
        "task_parameters": task_parameters,
        "skill": SKILL,
        "max_retries": max_retries,
        "max_wait": max_wait,
        "parse_response": parse_response
    }

    # Run skill:
    return run_language_skill(skill_config=skill_config)
