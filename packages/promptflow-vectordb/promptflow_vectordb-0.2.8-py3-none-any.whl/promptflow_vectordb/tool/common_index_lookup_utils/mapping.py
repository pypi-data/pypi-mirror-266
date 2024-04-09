from .constants import IndexTypes, EmbeddingTypes
from .mlindex_client import MLIndexClient
from .utils import CallbackContext, tool_ui_callback

from azureml.rag.mlindex import MLIndex
from azureml.rag.embeddings import EmbeddingsContainer
from io import StringIO
import os
from ruamel.yaml import YAML
from typing import Any, Dict
import tempfile

yaml = YAML()


@tool_ui_callback
def forward_mapping(
    context: CallbackContext,
    index_type: str,
    mlindex_asset_id: str = None,
    mlindex_path: str = None,
    acs_index_connection: str = None,
    acs_index_name: str = None,
    acs_content_field: str = None,
    acs_embedding_field: str = None,
    acs_metadata_field: str = None,
    semantic_configuration: str = None,
    faiss_index_path: str = None,
    pinecone_index_connection: str = None,
    pinecone_index_name: str = None,
    pinecone_content_field: str = None,
    pinecone_metadata_field: str = None,
    embedding_type: str = None,
    aoai_embedding_connection: str = None,
    oai_embedding_connection: str = None,
    embedding_model: str = None,
    embedding_deployment: str = None,
    serverless_embedding_connection: str = None
) -> str:
    if index_type in {IndexTypes.MLIndexAsset, IndexTypes.MLIndexPath}:
        mlindex_client = MLIndexClient(context)
        if index_type == IndexTypes.MLIndexAsset:

            asset_id_parts = mlindex_asset_id.split('/')
            asset_name = asset_id_parts[7]
            asset_version = asset_id_parts[9]

            data_asset_obj = context.ml_client.data.get(asset_name, asset_version)
            mlindex_content = mlindex_client.get_mlindex_content(data_asset_obj.path, mlindex_asset_id)
            mlindex_path = data_asset_obj.path

        if index_type == IndexTypes.MLIndexPath:
            mlindex_content = mlindex_client.get_mlindex_content(mlindex_path)

        try:
            mlindex_config = yaml.load(mlindex_content)
            if (
                mlindex_config.get("index", {}).get("kind") == "faiss"
                and mlindex_config.get("index", {}).get("path") is None
            ):
                mlindex_config["index"]["path"] = mlindex_path
                with StringIO() as stream:
                    yaml.dump(mlindex_config, stream)
                    mlindex_content = stream.getvalue()
        except Exception as e:
            raise ValueError(f'Failed to process mlindex content with exception: { e }')

        return mlindex_content

    elif index_type in {IndexTypes.AzureCognitiveSearch , IndexTypes.FAISS, IndexTypes.Pinecone}:
        mlindex_config = {
            'index': _get_index_config(
                context,
                index_type,
                acs_index_connection,
                acs_index_name,
                acs_content_field,
                acs_embedding_field,
                acs_metadata_field,
                semantic_configuration,
                faiss_index_path,
                pinecone_index_connection,
                pinecone_index_name,
                pinecone_content_field,
                pinecone_metadata_field),
            'embeddings': get_embeddings_config(
                context,
                embedding_type,
                aoai_embedding_connection,
                oai_embedding_connection,
                embedding_model,
                embedding_deployment,
                serverless_embedding_connection),
        }

        mlindex = MLIndex(mlindex_config=mlindex_config)
        with tempfile.TemporaryDirectory() as staging_dir:
            mlindex.save(staging_dir, just_config=True)
            with open(os.path.join(staging_dir, 'MLIndex'), 'r', encoding='utf-8') as src:
                return src.read()

    else:
        raise ValueError(f'Unexpected index type: {index_type}')


@tool_ui_callback
def reverse_mapping(context: CallbackContext, mlindex_content: str) -> Dict[str, Any]:
    with StringIO(mlindex_content) as stream:
        mlindex_config = yaml.load(stream)

    mlindex = MLIndex(mlindex_config=mlindex_config)

    index_kind = mlindex.index_config.get("kind", "none")
    if index_kind == "acs":
        mapped_index_args = {
            "index_type": IndexTypes.AzureCognitiveSearch,
            "acs_index_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "acs_index_name": mlindex.index_config.get("index"),
            "acs_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "acs_embedding_field": mlindex.index_config.get("field_mapping", {}).get(
                "embedding"
            ),
            "acs_metadata_field": mlindex.index_config.get("field_mapping", {}).get(
                "metadata"
            ),
            "semantic_configuration": mlindex.index_config.get(
                "semantic_configuration_name"
            ),
        }
    elif index_kind == "faiss":
        mapped_index_args = {
            "index_type": IndexTypes.FAISS,
            "faiss_index_path": mlindex.index_config.get("path"),
        }
    elif index_kind == "pinecone":
        mapped_index_args = {
            "index_type": IndexTypes.Pinecone,
            "pinecone_index_connection": mlindex.index_config.get("connection", {})
            .get("id", "")
            .split("/")[-1],
            "pinecone_index_name": mlindex.index_config.get("index"),
            "pinecone_content_field": mlindex.index_config.get("field_mapping", {}).get(
                "content"
            ),
            "pinecone_metadata_field": mlindex.index_config.get(
                "field_mapping", {}
            ).get("metadata"),
        }
    else:
        raise NotImplementedError(f'"{index_kind}" is not a supported index kind.')

    embedding_kind = mlindex.embeddings_config.get("kind")
    embedding_api_type = mlindex.embeddings_config.get("api_type")
    if embedding_kind == "none":
        mapped_embedding_args = {
            "embedding_type": EmbeddingTypes.NoEmbedding,
        }
    elif embedding_kind == "open_ai":
        if embedding_api_type == "azure":
            mapped_embedding_args = {
                "embedding_type": EmbeddingTypes.AzureOpenAI,
                "aoai_embedding_connection": mlindex.embeddings_config.get(
                    "connection", {}
                )
                .get("id", "")
                .split("/")[-1],
                "embedding_deployment": mlindex.embeddings_config.get("deployment"),
            }
        else:
            raise NotImplementedError(
                '"azure" is the only supported value for embedding api_type.'
            )
    elif embedding_kind == "serverless_endpoint":
        mapped_embedding_args = {
            "embedding_type": EmbeddingTypes.ServerlessEndpoint,
            "serverless_embedding_connection": mlindex.embeddings_config.get(
                "connection", {}
            )
            .get("id", "")
            .split("/")[-1],
        }
    elif embedding_kind == "hugging_face":
        mapped_embedding_args = {
            "embedding_type": EmbeddingTypes.HuggingFace,
            "embedding_model": mlindex.embedding_configs.get("model"),
        }
    else:
        raise NotImplementedError(
            f'"{embedding_kind}" embedding kind is not currently supported'
        )

    return {**mapped_index_args, **mapped_embedding_args}


def get_embeddings_config(
    context: CallbackContext,
    embedding_type: str = None,
    aoai_embedding_connection: str = None,
    oai_embedding_connection: str = None,
    embedding_model: str = None,
    embedding_deployment: str = None,
    serverless_embedding_connection: str = None,
) -> Dict[str, Any]:
    if not embedding_type or embedding_type == EmbeddingTypes.NoEmbedding:
        return {
            "kind": "none",
            "schema_version": "2",
        }

    elif embedding_type == EmbeddingTypes.AzureOpenAI:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=aoai_embedding_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        resolved_embedding_model = _get_embedding_model(
            context, selected_connection, embedding_deployment
        )
        embeddings_config = {
            "kind": "open_ai",
            "api_type": "azure",
            "api_base": selected_connection.properties.target,
            "api_version": selected_connection.properties.metadata.get(
                "ApiVersion", "2023-03-15-preview"
            ),
            "batch_size": "1",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "deployment": embedding_deployment,
            "model": resolved_embedding_model,
            "schema_version": "2",
        }

    elif embedding_type == EmbeddingTypes.OpenAI:
        raise NotImplementedError()

    elif embedding_type == EmbeddingTypes.ServerlessEndpoint:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=serverless_embedding_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        embeddings_config = {
            "kind": "serverless_endpoint",
            "api_type": selected_connection.properties.metadata.get("MODEL_PROVIDER_NAME", "cohere").lower(),
            "api_base": selected_connection.properties.target,
            "model": selected_connection.properties.metadata.get("SERVED_MODEL_NAME", "cohere-embed-english"),
            "batch_size": "1",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "schema_version": "2",
        }

    elif embedding_type == EmbeddingTypes.HuggingFace:
        embeddings_config = {
            "kind": "hugging_face",
            "model": embedding_model,
            "schema_version": "2",
        }

    else:
        raise ValueError(f"Unexpected embedding type: {embedding_type}")

    embedder = EmbeddingsContainer.from_metadata(embeddings_config.copy()).get_query_embed_fn()
    embeddings_config["dimension"] = len(embedder("hello world!"))
    return embeddings_config


def _get_index_config(
    context: CallbackContext,
    index_type: str,
    acs_index_connection: str = None,
    acs_index_name: str = None,
    acs_content_field: str = None,
    acs_embedding_field: str = None,
    acs_metadata_field: str = None,
    semantic_configuration: str = None,
    faiss_index_path: str = None,
    pinecone_index_connection: str = None,
    pinecone_index_name: str = None,
    pinecone_content_field: str = None,
    pinecone_metadata_field: str = None,
) -> Dict[str, Any]:
    if index_type == IndexTypes.AzureCognitiveSearch:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=acs_index_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "acs",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "endpoint": selected_connection.properties.target,
            "api_version": selected_connection.properties.metadata.get(
                "ApiVersion", "2023-07-01-preview"
            ),
            "engine": "azure-sdk",
            "field_mapping": {
                "content": acs_content_field,
                "embedding": acs_embedding_field,
                "metadata": acs_metadata_field,
            },
            "index": acs_index_name,
            "semantic_configuration_name": semantic_configuration,
        }

    if index_type == IndexTypes.FAISS:
        return {
            "kind": "faiss",
            "engine": "langchain.vectorstores.FAISS",
            "method": "flatL2",
            "path": faiss_index_path,
        }

    if index_type == IndexTypes.Pinecone:
        selected_connection = context.ml_client.connections._operation.get(
            workspace_name=context.workspace_name,
            connection_name=pinecone_index_connection,
            **context.ml_client.connections._scope_kwargs,
        )

        return {
            "kind": "pinecone",
            "connection": {
                "id": selected_connection.id,
            },
            "connection_type": "workspace_connection",
            "engine": "azure-sdk",
            "index": pinecone_index_name,
            "field_mapping": {
                "content": pinecone_content_field,
                "metadata": pinecone_metadata_field,
            },
        }

    raise ValueError(f"Unexpected index type: {index_type}")


def _get_embedding_model(
    context: CallbackContext, selected_connection, deployment_name: str
) -> str:
    deployment_url = (
        f'https://management.azure.com{selected_connection.properties.metadata.get("ResourceId")}'
        + f"/deployments/{deployment_name}?api-version=2023-05-01"
    )
    auth_header = f'Bearer {context.credential.get_token("https://management.azure.com/.default").token}'
    deployment = context.http.get(
        deployment_url, headers={"Authorization": auth_header}
    ).json()

    return deployment.get("properties", {}).get("model", {}).get("name")
