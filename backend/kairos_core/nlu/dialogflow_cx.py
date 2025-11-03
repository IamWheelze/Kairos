from __future__ import annotations

import asyncio
import uuid
from typing import Optional

from google.cloud import dialogflowcx_v3 as dialogflowcx

from kairos_core.config import get_settings
from kairos_core.nlu.interfaces import NLUClient, NLUResult


class DialogflowCXClient(NLUClient):
    def __init__(self) -> None:
        self.settings = get_settings()
        if not (self.settings.dialogflow_project_id and self.settings.dialogflow_location and self.settings.dialogflow_agent_id):
            raise RuntimeError("Dialogflow settings incomplete")
        self._client = dialogflowcx.SessionsClient()

    async def detect_intent(self, text: str, context: Optional[dict] = None) -> NLUResult:
        return await asyncio.get_event_loop().run_in_executor(None, self._detect_sync, text, context or {})

    def _detect_sync(self, text: str, context: dict) -> NLUResult:
        session_path = self._client.session_path(
            project=self.settings.dialogflow_project_id,
            location=self.settings.dialogflow_location,
            agent=self.settings.dialogflow_agent_id,
            session=str(uuid.uuid4()),
        )
        text_input = dialogflowcx.TextInput(text=text)
        query_input = dialogflowcx.QueryInput(text=text_input, language_code="en-US")

        # Optional: set parameters from context
        params = None
        if context:
            params = dialogflowcx.SessionParameters(fields={k: dialogflowcx.types.Value(string_value=str(v)) for k, v in context.items()})

        request = dialogflowcx.DetectIntentRequest(
            session=session_path,
            query_input=query_input,
            parameters=params,
        )
        response = self._client.detect_intent(request=request)

        # Map result
        intent_name = "Fallback"
        confidence = 0.0
        parameters: dict = {}
        if response.query_result and response.query_result.intent:
            intent = response.query_result.intent
            # Only the display_name is meaningful for mapping
            intent_name = intent.display_name or intent.name or "Fallback"
            # Confidence lives in match confidence if available
            confidence = float(getattr(response.query_result.match, "confidence", 0.0))
        # Extract parameters
        if response.query_result and response.query_result.parameters:
            for k, v in response.query_result.parameters.fields.items():
                if v.string_value:
                    parameters[k] = v.string_value

        return NLUResult(intent=intent_name, params=parameters, confidence=confidence)

