#
# Copyright 2024 DataRobot, Inc. and its affiliates.
#
# All rights reserved.
#
# DataRobot, Inc.
#
# This is proprietary source code of DataRobot, Inc. and its
# affiliates.
#
# Released under the terms of DataRobot Tool and Utility Agreement.
from __future__ import annotations

from typing import Any, Dict, List, Optional

import trafaret as t

from datarobot._experimental.models.genai.chat_prompt import (
    confidence_scores_trafaret,
    result_metadata_trafaret,
)
from datarobot._experimental.models.genai.llm_blueprint import vector_database_settings_trafaret
from datarobot.models.api_object import APIObject
from datarobot.utils.pagination import unpaginate

datarobot_user = t.Dict(
    {
        t.Key("id"): t.String,
        t.Key("name"): t.String,
    }
)

prompt_trace = t.Dict(
    {
        t.Key("timestamp"): t.String,
        t.Key("user"): datarobot_user,
        t.Key("chat_prompt_id", optional=True): t.Or(t.String, t.Null),
        t.Key("use_case_id", optional=True): t.Or(t.String, t.Null),
        t.Key("comparison_prompt_id", optional=True): t.Or(t.String, t.Null),
        t.Key("llm_blueprint_id"): t.String,
        t.Key("llm_name"): t.String,
        t.Key("llm_vendor"): t.String,
        t.Key("llm_license"): t.String,
        t.Key("llm_settings", optional=True): t.Or(t.Dict().allow_extra("*"), t.Null),
        t.Key("vector_database_id", optional=True): t.Or(t.String, t.Null),
        t.Key("vector_database_settings", optional=True): t.Or(
            vector_database_settings_trafaret, t.Null
        ),
        t.Key("result_metadata", optional=True): t.Or(result_metadata_trafaret, t.Dict()),
        t.Key("result_text", optional=True): t.Or(t.String, t.Null),
        t.Key("confidence_scores", optional=True): t.Or(confidence_scores_trafaret, t.Null),
        t.Key("text"): t.String,
        t.Key("execution_status"): t.String,
    }
)


class PromptTrace(APIObject):
    """
    Prompt trace contains aggregated information about a prompt execution.

    Attributes
    ----------
    timestamp : str
        The timestamp of the trace (ISO 8601 formatted).
    user : dict
        The user who submitted the prompt.
    chat_prompt_id : str
        The ID of the chat prompt associated with the trace.
    use_case_id : str
        The ID of the Use Case the playground is in.
    comparison_prompt_id : str
        The ID of the comparison prompts associated with the trace.
    llm_blueprint_id : str
        The ID of the LLM blueprint that the prompt was submitted to.
    llm_name : str
        The name of the LLM in the LLM blueprint.
    llm_vendor : str
        The vendor name of the LLM.
    llm_license : str
        What type of license the LLM has.
    llm_settings : dict
        The LLM settings for the LLM blueprint. The specific keys allowed and the
        constraints on the values are defined in the response from LLMDefinition.list
        but this typically has dict fields:
        - system_prompt - The system prompt that tells the LLM how to behave.
        - max_completion_length - The maximum number of token in the completion.
        - temperature - Controls the variability in the LLM response.
        - top_p - The model considers next tokens with top_p probability mass
        - system_prompt - The system prompt that tells the LLM how to behave.
        - validation_id - The ID of the custom model LLM validation
        for custom model LLM blueprints.
    vector_database_id : str or None
        ID of the vector database associated with the LLM blueprint, if any.
    vector_database_settings : VectorDatabaseSettings or None
        The settings for the vector database associated with the LLM blueprint, if any.
    result_metadata : ResultMetadata or None
        Metadata for the result of the prompt submission.
    result_text: str or None
        The result text from the prompt submission.
    confidence_scores: ConfidenceScores or None
        The confidence scores if there is a vector database associated with the prompt.
    text: str
        The prompt text submitted to the LLM.
    execution_status: str
        The execution status of the chat prompt.
    """

    _path = "api-gw/genai/playgrounds/{}/trace/"
    _export_path = "api-gw/genai/playgrounds/{}/traceDatasets/"

    _converter = prompt_trace

    def __init__(
        self,
        timestamp: str,
        user: Dict[str, str],
        use_case_id: str,
        llm_blueprint_id: str,
        llm_name: str,
        llm_vendor: str,
        llm_license: str,
        text: str,
        execution_status: str,
        chat_prompt_id: Optional[str] = None,
        comparison_prompt_id: Optional[str] = None,
        llm_settings: Optional[Dict[str, Any]] = None,
        vector_database_id: Optional[str] = None,
        vector_database_settings: Optional[Dict[str, Any]] = None,
        result_metadata: Optional[Dict[str, Any]] = None,
        result_text: Optional[str] = None,
        confidence_scores: Optional[Dict[str, float]] = None,
    ):
        self.timestamp = timestamp
        self.user = user
        self.chat_prompt_id = (chat_prompt_id,)
        self.use_case_id = use_case_id
        self.comparison_prompt_id = comparison_prompt_id
        self.llm_blueprint_id = llm_blueprint_id
        self.llm_name = llm_name
        self.llm_vendor = llm_vendor
        self.llm_license = llm_license
        self.llm_settings = llm_settings
        self.vector_database_id = vector_database_id
        self.vector_database_settings = vector_database_settings
        self.result_metadata = result_metadata
        self.result_text = result_text
        self.confidence_scores = confidence_scores
        self.text = text
        self.execution_status = execution_status

    @classmethod
    def list(cls, playground_id: str) -> List[PromptTrace]:
        """
        List all prompt traces for a playground.

        Parameters
        ----------
        playground_id: str
            The ID of the playground to list prompt traces for.

        Returns
        -------
        prompt_traces: list[PromptTrace]
            List of prompt traces for the playground.
        """
        url = f"{cls._client.domain}/{cls._path.format(playground_id)}"
        response = unpaginate(url, None, cls._client)
        return [cls.from_server_data(trace) for trace in response]

    @classmethod
    def export_to_ai_catalog(cls, playground_id: str) -> Any:
        """
        Export prompt traces to AI Catalog as a CSV.

        Parameters
        ----------
        playground_id: str
            The ID of the playground to export prompt traces for.

        Returns
        -------
        status_url: str
            The URL where the status of the job can be monitored
        """
        url = f"{cls._client.domain}/{cls._export_path.format(playground_id)}"
        response = cls._client.post(url)
        return response.headers["Location"]
