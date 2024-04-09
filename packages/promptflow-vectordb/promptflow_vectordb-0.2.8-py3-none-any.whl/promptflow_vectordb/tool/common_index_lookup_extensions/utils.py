from .acs import simple_search_with_score, semantic_search_with_score

from ..common_index_lookup_utils.constants import QueryTypes

from azureml.rag import MLIndex
import functools
from langchain.docstore.document import Document
from typing import Callable, List, Tuple


def build_search_func(index: MLIndex, top_k: int, query_type: str) -> Callable[[str], List[Tuple[Document, float]]]:
    # Override the embeddings section if we're making keyword queries.
    if query_type in {QueryTypes.Simple, QueryTypes.Semantic}:
        index.embeddings_config = {
            'schema_version': '2',
            'kind': 'none'
        }

        # Temporary workaround for `as_langchain_vectorstore` throwing when field_mapping.embedding is None.
        if 'field_mapping' in index.index_config:
            index.index_config['field_mapping']['embedding'] = ''

    index_kind = index.index_config.get("kind", "none")
    store = index.as_langchain_vectorstore()

    if index_kind == 'acs':
        if query_type == QueryTypes.Simple:
            return functools.partial(
                simple_search_with_score,
                store=store,
                k=top_k,
                field_mapping=index.index_config.get('field_mapping')
            )

        if query_type == QueryTypes.Semantic:
            return functools.partial(
                semantic_search_with_score,
                store=store,
                k=top_k,
                field_mapping=index.index_config.get('field_mapping'),
                hybrid=False
            )

        if query_type == QueryTypes.Vector:
            # AzureSearch doesn't implement similiarity_search_with_score
            return functools.partial(store.vector_search_with_score, k=top_k)

        if query_type == QueryTypes.VectorSimpleHybrid:
            return functools.partial(store.hybrid_search_with_score, k=top_k)

        if query_type == QueryTypes.VectorSemanticHybrid:
            return functools.partial(
                semantic_search_with_score,
                store=store,
                k=top_k,
                field_mapping=index.index_config.get('field_mapping'),
                hybrid=True
            )
    else:
        if query_type == QueryTypes.Vector:
            return functools.partial(store.similarity_search_with_score, k=top_k)

    raise ValueError(f'Unsupported query type: {query_type} for index kind {index_kind}.')
