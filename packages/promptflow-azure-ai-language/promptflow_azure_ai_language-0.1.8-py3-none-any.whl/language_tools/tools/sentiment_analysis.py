# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from promptflow import tool
from promptflow.connections import CustomConnection
from language_utils.language_skill import LanguageSkill
from language_utils.language_tool_utils import run_language_skill

API_VERSION = "2023-11-15-preview"
SKILL = LanguageSkill.SENTIMENT_ANALYSIS


@tool
def get_sentiment_analysis(connection: CustomConnection,
                           document: dict,
                           opinion_mining: bool = False,
                           max_retries: int = 5,
                           max_wait: int = 60,
                           parse_response: bool = False):
    # Create query parameters:
    query_parameters = {
        "api-version": API_VERSION,
    }

    # Create task parameters:
    task_parameters = {
        "opinionMining": opinion_mining
    }

    # Create skill config:
    skill_config = {
        "connection": connection,
        "query_parameters": query_parameters,
        "input": document,
        "task_parameters": task_parameters,
        "skill": SKILL,
        "max_retries": max_retries,
        "max_wait": max_wait,
        "parse_response": parse_response
    }

    # Run skill:
    return run_language_skill(skill_config=skill_config)
