class IndexTypes(str):
    AzureCognitiveSearch = "Azure AI Search"
    FAISS = "FAISS"
    Pinecone = "Pinecone"
    MLIndexAsset = "Registered Index"
    MLIndexPath = "MLIndex file from path"


class EmbeddingTypes(str):
    NoEmbedding = "None"
    AzureOpenAI = "Azure OpenAI"
    OpenAI = "OpenAI"
    HuggingFace = "Hugging Face"
    ServerlessEndpoint = "Serverless Endpoint"


class QueryTypes(str):
    Simple = "Keyword"
    Semantic = "Semantic"
    Vector = "Vector"
    VectorSimpleHybrid = "Hybrid (vector + keyword)"
    VectorSemanticHybrid = "Hybrid + semantic"


class LoggingEvents(str):
    SearchFunctionConstruction = "search_function_construction"
    SearchFunctionExecution = "search_function_execution"
    SearchFunctionInnerExecution = "search_function_inner_execution"
    AzureMLRagSearch = "azureml_rag_search"
    TelemetryWrapperConstruction = "telemetry_wrapper_construction"


class LoggerNames(str):
    PromptflowTool = "promptflow_tool"
    AzureMLRAG = "azureml_rag"
