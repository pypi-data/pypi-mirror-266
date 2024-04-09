import contextvars
import json
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
import logging
import os
from typing import List, Union

from azureml.rag.mlindex import MLIndex
from opentelemetry import trace
from promptflow import tool
from promptflow.exceptions import UserErrorException
from ruamel.yaml import YAML

from ..core.logging.utils import LoggingUtils
from .common_index_lookup_extensions import build_search_func
from .common_index_lookup_utils.constants import LoggerNames, LoggingEvents
from .common_index_lookup_utils.logger import (
    get_lookup_logger,
    enable_rag_logger,
    track_rag_activity,
)
from .utils.profiling import measure_execution_time


__LOG_LEVEL_ENV_KEY = "PF_LOGGING_LEVEL"
try:
    __LOG_LEVEL_MAPPINGS = logging.getLevelNamesMapping()
except AttributeError:
    # logging.getLevelNamesMapping was only introduced in 3.11; fallback for older versions
    __LOG_LEVEL_MAPPINGS = {
        "CRITICAL": logging.CRITICAL,
        "ERROR": logging.ERROR,
        "WARNING": logging.WARNING,
        "INFO": logging.INFO,
        "DEBUG": logging.DEBUG,
    }

tracer = trace.get_tracer(__name__)
yaml = YAML()

pf_tool_logger = get_lookup_logger(
    LoggerNames.PromptflowTool,
    log_level=__LOG_LEVEL_MAPPINGS.get(os.getenv(__LOG_LEVEL_ENV_KEY), logging.INFO),
)
rag_logger = get_lookup_logger(LoggerNames.AzureMLRAG)


@lru_cache(maxsize=32)
def _get_search_func(mlindex_content: str, top_k: int, query_type: str):
    with measure_execution_time(LoggingEvents.SearchFunctionConstruction):
        mlindex_config = yaml.load(mlindex_content)
        index = MLIndex(mlindex_config=mlindex_config)
        search_func = build_search_func(index, top_k, query_type)

    with measure_execution_time(LoggingEvents.TelemetryWrapperConstruction):

        def telemetry_wrapper(query: str):
            with tracer.start_as_current_span("search") as span:
                span.set_attribute("span_type", "Retrieval")
                span.set_attribute("retrieval.query", query)
                with measure_execution_time(LoggingEvents.SearchFunctionInnerExecution):
                    search_result = search_func(query)

                try:
                    loggable_results = [
                        {
                            "document.content": doc.page_content,
                            "document.score": score,
                            "document.metadata": doc.metadata,
                        }
                        for doc, score in search_result
                    ]
                    span.set_attribute(
                        "retrieval.documents", json.dumps(loggable_results)
                    )
                except Exception as ex:
                    span.set_attribute(
                        "retrieval.documents.serialization_error", str(ex)
                    )
                return search_result

        return telemetry_wrapper


def _set_context_vars(context: contextvars.Context):
    for var, value in context.items():
        var.set(value)


@tool
@LoggingUtils.log_event(
    package_name=__package__,
    event_name=LoggingEvents.AzureMLRagSearch,
    logger=pf_tool_logger,
    flush=True,
)
def search(
    mlindex_content: str,
    queries: Union[str, List[str]],
    top_k: int,
    query_type: str,
) -> List[List[dict]]:

    log_level = __LOG_LEVEL_MAPPINGS.get(os.getenv(__LOG_LEVEL_ENV_KEY), logging.INFO)
    enable_rag_logger(log_level)

    with track_rag_activity(rag_logger, LoggingEvents.AzureMLRagSearch):
        if isinstance(queries, str):
            queries = [queries]
            unwrap = True
        elif isinstance(queries, list) and all([isinstance(q, str) for q in queries]):
            unwrap = False
        elif isinstance(queries, list) and all([isinstance(q, float) for q in queries]):
            raise UserErrorException(
                "Expected input type to be either `str` or `List[str]`, found `List[float]`."
                " Did you perhaps pass in an embedding vector instead of a string query?"
            )
        else:
            raise UserErrorException(
                "Expected input type to be either `str` or `List[str]`."
            )

        search_func = _get_search_func(mlindex_content, top_k, query_type)

        parent_context = contextvars.copy_context()
        with measure_execution_time(LoggingEvents.SearchFunctionExecution):
            with ThreadPoolExecutor(
                initializer=_set_context_vars, initargs=(parent_context,)
            ) as search_executor:
                search_results = search_executor.map(search_func, queries)
                results = [
                    [
                        {
                            "text": doc.page_content,
                            "metadata": doc.metadata,
                            "score": score,
                        }
                        for doc, score in search_result
                    ]
                    for search_result in search_results
                ]

    if unwrap and len(results) == 1:
        return results[0]
    else:
        return results
