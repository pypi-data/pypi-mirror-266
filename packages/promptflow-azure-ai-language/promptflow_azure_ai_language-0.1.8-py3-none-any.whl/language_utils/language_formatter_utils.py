# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
import time
from language_utils.language_skill import LanguageSkill
from language_utils.language_mode import LanguageMode


# Creates a simple task name given a skill and id.
# e.g. "AbstractiveSummarization Task 1"
def create_task_name(skill: LanguageSkill, id: int) -> str:
    return LanguageSkill.to_str(skill) + " Task " + str(id)


# Formats a task with its kind and name.
def format_task(task: dict) -> dict:
    skill = task["skill"]
    del task["skill"]
    task["kind"] = LanguageSkill.to_str(skill)
    task["taskName"] = create_task_name(skill, 1)
    return task


# Function to obtain "analysisInput" field of API input based on skill.
def analysis_input_func(skill: LanguageSkill):
    # CLU is special case:
    if skill == LanguageSkill.CONVERSATIONAL_LANGUAGE_UNDERSTANDING:
        return lambda conv_item: {"conversationItem": conv_item}
    elif LanguageSkill.is_conversational(skill):
        return lambda conversation: {"conversations": [conversation]}
    else:
        return lambda document: {"documents": [document]}


# Function to format sync input based on skill.
def format_sync_func(skill: LanguageSkill):
    if skill == LanguageSkill.TRANSLATION:
        return lambda input, _: [input]
    return lambda input, parameters: {
        "kind": LanguageSkill.to_str(skill),
        "analysisInput": analysis_input_func(skill)(input),
        "parameters": parameters
    }


# Function to format async input based on skill.
def format_async_func(skill: LanguageSkill):
    return lambda input, parameters: {
        "displayName": LanguageSkill.to_str(skill) + "Job:" + str(time.time()),
        "analysisInput": analysis_input_func(skill)(input),
        "tasks": [format_task({"skill": skill, "parameters": parameters})]
    }


# Format input based on skill and mode.
def format_input(input: dict,
                 parameters: dict,
                 skill: LanguageSkill,
                 mode: LanguageMode) -> dict:
    if mode == LanguageMode.SYNC:
        format_func = format_sync_func(skill)
    else:
        format_func = format_async_func(skill)
    return format_func(input, parameters)
