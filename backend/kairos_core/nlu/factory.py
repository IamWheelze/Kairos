from __future__ import annotations

import os
from typing import Optional

from kairos_core.config import get_settings
from kairos_core.nlu.interfaces import NLUClient
from kairos_core.nlu.rule_based import RuleBasedNLU
from kairos_core.nlu.dialogflow_cx import DialogflowCXClient


def get_nlu_client() -> NLUClient:
    settings = get_settings()
    # Placeholder: return Dialogflow client when configured
    if (
        settings.dialogflow_project_id
        and settings.dialogflow_location
        and settings.dialogflow_agent_id
        and os.getenv("GOOGLE_APPLICATION_CREDENTIALS")
    ):
        try:
            return DialogflowCXClient()
        except Exception:
            # Fallback to rule-based if config/creds incomplete
            return RuleBasedNLU()
    return RuleBasedNLU()
