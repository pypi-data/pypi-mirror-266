# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import json
from promptflow import tool
from promptflow.connections import CustomConnection
from language_utils.language_skill import LanguageSkill
from language_utils.language_tool_utils import run_language_skill

API_VERSION = "2023-04-15-preview"
SKILL = LanguageSkill.CONVERSATIONAL_LANGUAGE_UNDERSTANDING


@tool
def get_conversational_language_understanding(connection: CustomConnection,
                                              language: str,
                                              utterances: str,
                                              project_name: str,
                                              deployment_name: str,
                                              max_retries: int = 5,
                                              max_wait: int = 60,
                                              parse_response: bool = False):
    utteranceList = []
    try:
        utteranceList = json.loads(utterances)
    except ValueError:  # includes JSONDecodeError.
        utteranceList.append(utterances)
    results = []
    for id, utterance in enumerate(utteranceList):
        results.append(get_single_clu_result(
            connection,
            language,
            utterance,
            project_name,
            deployment_name,
            id,
            max_retries,
            max_wait,
            parse_response
        ))
    return results


def get_single_clu_result(connection: CustomConnection,
                          language: str,
                          text: str,
                          project_name: str,
                          deployment_name: str,
                          id: int,
                          max_retries: int,
                          max_wait: int,
                          parse_response: bool = False) -> str:
    # Create input:
    conv_item = {
        "text": text,
        "language": language,
        "modality": "text",
        "id": str(id),
        "participantId": str(id)
    }

    # Create query parameters:
    query_parameters = {
        "api-version": API_VERSION,
    }

    # Create task parameters:
    task_parameters = {
        "projectName": project_name,
        "deploymentName": deployment_name,
        "verbose": True
    }

    # Create tool config:
    skill_config = {
        "connection": connection,
        "query_parameters": query_parameters,
        "input": conv_item,
        "task_parameters": task_parameters,
        "skill": SKILL,
        "max_retries": max_retries,
        "max_wait": max_wait,
        "parse_response": parse_response
    }

    # Run tool:
    return run_language_skill(skill_config=skill_config)
