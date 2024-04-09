# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from language_utils.language_skill import LanguageSkill
from language_utils.language_mode import LanguageMode


# Obtains 'results' field from an async response with a single task.
def get_async_results(response: dict):
    if response["status"] == "failed":
        errors = response["errors"]
        print(f"Task failure: {errors}")
        raise RuntimeError(errors)

    return response["tasks"]["items"][0]["results"]


# Obtains 'results' field from an sync response.
def get_sync_results(response: dict):
    if "results" in response:
        return response["results"]
    else:
        # Special case: Translator & CLU:
        return response


# Get reponse results based on mode.
def get_results(response: dict, mode: LanguageMode):
    if mode == LanguageMode.SYNC:
        return get_sync_results(response)
    else:
        return get_async_results(response)


# Get single task result based on if input was a document or conversation.
def get_task_result(results: dict, skill: LanguageSkill):
    if "errors" in results and len(results["errors"]) != 0:
        errors = results["errors"]
        print(f"API Result Errors: {errors}")
        return RuntimeError(str(errors))

    # CLU is special case:
    if skill == LanguageSkill.CONVERSATIONAL_LANGUAGE_UNDERSTANDING:
        return results["result"]
    elif LanguageSkill.is_conversational(skill):
        return results["conversations"][0]
    elif skill == LanguageSkill.TRANSLATION:
        return results[0]
    else:
        return results["documents"][0]


# Parse API response to extract singular task result.
def parse_response(response: dict, skill: LanguageSkill, mode: LanguageMode):
    try:
        results = get_results(response, mode)
        return get_task_result(results, skill)
    except (KeyError, ValueError, RuntimeError) as error:
        print(f"Unable to parse API response: {error}")
        return error
