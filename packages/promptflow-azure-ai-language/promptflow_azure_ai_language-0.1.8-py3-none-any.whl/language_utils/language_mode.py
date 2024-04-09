# ---------------------------------------------------------
# Copyright (c) Microsoft Corporation. All rights reserved.
# ---------------------------------------------------------
from enum import Enum


# Azure AI Language API Mode:
class LanguageMode(Enum):
    SYNC = 0
    ASYNC = 1
