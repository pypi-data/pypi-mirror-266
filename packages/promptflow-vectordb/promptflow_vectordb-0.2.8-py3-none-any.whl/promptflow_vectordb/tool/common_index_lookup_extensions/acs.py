import json
from langchain.docstore.document import Document
from typing import Dict, List, Optional, Tuple, Union


def simple_search_with_score(
        query: str,
        store: "langchain.vectorstores.AzureSearch",
        k: int = 4,
        field_mapping: Dict[str, str] = None,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "contentVector"
    metadata_field = (field_mapping or {}).get("metadata") or "meta_json_string"

    results = store.client.search(
        search_text=query,
        query_type='simple',
        filter=filters,
        top=k,
    )

    # Convert results to Document objects
    docs = [
        (
            Document(
                page_content=result.pop(content_field),
                metadata=json.loads(result[metadata_field])
                if metadata_field in result
                else {k: v for k, v in result.items() if k != embedding_field},
            ),
            float(result['@search.score']),
        )
        for result in results
    ]

    return docs


def semantic_search_with_score(
        query: str,
        store: "langchain.vectorstores.AzureSearch",
        k: int = 4,
        hybrid: bool = False,
        field_mapping: Dict[str, str] = None,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "contentVector"
    metadata_field = (field_mapping or {}).get("metadata") or "meta_json_string"

    if hybrid:
        from azure.search.documents.models import Vector
        import numpy as np
        results = store.client.search(
            search_text=query,
            vectors=[
                Vector(
                    value=np.array(
                        store.embedding_function(query), dtype=np.float32
                    ).tolist(),
                    k=50,
                    fields=embedding_field,
                )
            ],
            filter=filters,
            query_type='semantic',
            query_language=store.semantic_query_language,
            semantic_configuration_name=store.semantic_configuration_name,
            query_caption='extractive',
            query_answer='extractive',
            top=k,
        )
    else:
        results = store.client.search(
            search_text=query,
            filter=filters,
            query_type='semantic',
            query_language=store.semantic_query_language,
            semantic_configuration_name=store.semantic_configuration_name,
            query_caption='extractive',
            query_answer='extractive',
            top=k,
        )

    # Get Semantic Answers
    semantic_answers = results.get_answers() or []
    semantic_answers_dict: Dict = {}
    for semantic_answer in semantic_answers:
        semantic_answers_dict[semantic_answer.key] = {
            'text': semantic_answer.text,
            'highlights': semantic_answer.highlights,
        }

    docs = [
        (
            Document(
                page_content=result.pop(content_field),
                metadata={
                    **(
                        json.loads(result[metadata_field])
                        if metadata_field in result
                        else {k: v for k, v in result.items() if k != embedding_field}
                    ),
                    **{
                        'captions': {
                            'text': result.get('@search.captions', [{}])[0].text,
                            'highlights': result.get('@search.captions', [{}])[
                                0
                            ].highlights,
                        }
                        if result.get('@search.captions')
                        else {},
                        'answers': semantic_answers_dict.get(
                            json.loads(result['metadata']).get('key'), ''
                        )
                        if result.get('metadata')
                        else {},
                    },
                },
            ),
            float(result['@search.score']),
        )
        for result in results
    ]

    return docs


def search_by_vector_with_score(
        vector: List[float],
        store: Union["langchain.vectorstores.AzureSearch", "langchain.vectorstores.FAISS"],
        kind: str,
        k: int = 4,
        field_mapping: Dict[str, str] = None,
        filters: Optional[str] = None
) -> List[Tuple[Document, float]]:
    """
    Support function supplying query-by-vector support for legacy lookup tools.
    Delete this function when decomissioning legacy tools.
    """
    from azure.search.documents.models import Vector
    import numpy as np

    content_field = (field_mapping or {}).get("content") or "content"
    embedding_field = (field_mapping or {}).get("embedding") or "contentVector"
    metadata_field = (field_mapping or {}).get("metadata") or "meta_json_string"

    if kind == "acs":
        results = store.client.search(
            search_text="",
            vectors=[
                Vector(
                    value=np.array(vector).tolist(),
                    k=k,
                    fields=embedding_field,
                )
            ],
            filter=filters,
        )

        # Convert results to Document objects
        docs = [
            (
                Document(
                    page_content=result.pop(content_field),
                    metadata=json.loads(result[metadata_field])
                    if metadata_field in result
                    else {
                        k: v for k, v in result.items() if k != embedding_field
                    },
                ),
                float(result["@search.score"]),
            )
            for result in results
        ]
        return docs

    elif kind == "faiss":
        return store.similarity_search_with_score_by_vector(vector, k=k, filter=filters)

    else:
        raise NotImplementedError(f"Unexpected index kind '{kind}'.")
