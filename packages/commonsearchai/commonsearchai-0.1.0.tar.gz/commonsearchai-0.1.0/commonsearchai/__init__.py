from azure.search.documents.indexes.models import (
    SearchIndex,
    SearchIndexer,
    SearchIndexerDataSourceConnection,
    SearchIndexerDataContainer,
    SearchField,
    SearchableField,
    SearchFieldDataType,
    VectorSearch,
    VectorSearchProfile,
    HnswAlgorithmConfiguration,
    AzureOpenAIEmbeddingSkill,
    SplitSkill
)
# Required to use the preview SDK
from azure.search.documents.indexes._generated.models import (
    SearchIndexerSkillset,
    AzureOpenAIVectorizer,
    AzureOpenAIParameters,
    SearchIndexerIndexProjections,
    SearchIndexerIndexProjectionSelector,
    SearchIndexerIndexProjectionsParameters,
    InputFieldMappingEntry,
    OutputFieldMappingEntry
)

def create_search_index(index_name, azure_openai_endpoint, azure_openai_embedding_deployment_id, azure_openai_key=None):
    return SearchIndex(
        name=index_name,
        fields=[
            SearchField(
                name="chunk_id",
                type=SearchFieldDataType.String,
                key=True,
                hidden=False,
                filterable=True,
                sortable=True,
                facetable=False,
                searchable=True,
                analyzer_name="keyword"
            ),
            SearchField(
                name="parent_id",
                type=SearchFieldDataType.String,
                hidden=False,
                filterable=True,
                sortable=True,
                facetable=False,
                searchable=True
            ),
            SearchField(
                name="chunk",
                type=SearchFieldDataType.String,
                hidden=False,
                filterable=False,
                sortable=False,
                facetable=False,
                searchable=True
            ),
            SearchField(
                name="title",
                type=SearchFieldDataType.String,
                hidden=False,
                filterable=False,
                sortable=False,
                facetable=False,
                searchable=True
            ),
            SearchField(
                name="vector",
                type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
                hidden=False,
                filterable=False,
                sortable=False,
                facetable=False,
                searchable=True,
                vector_search_dimensions=1536, 
                vector_search_profile_name="myHnswProfile"
            )
        ],
        vector_search=VectorSearch(
            profiles=[
                VectorSearchProfile(
                    name="myHnswProfile",
                    algorithm_configuration_name="hnsw-algorithm",
                    vectorizer="azure-openai-vectorizer"
                )
            ],
            algorithms=[
                HnswAlgorithmConfiguration(name="hnsw-algorithm")
            ],
            vectorizers=[
                AzureOpenAIVectorizer(
                        name="azure-openai-vectorizer",
                        azure_open_ai_parameters=AzureOpenAIParameters(
                            resource_uri=azure_openai_endpoint,
                            deployment_id=azure_openai_embedding_deployment_id,
                            api_key=azure_openai_key # Optional if using RBAC authentication
                        )
                    )
            ]
        )
    )

def create_search_datasource(datasource_name, connection_string, container_name):
    return SearchIndexerDataSourceConnection(
        name=datasource_name,
        type="azureblob",
        connection_string=connection_string,
        container=SearchIndexerDataContainer(
            name=container_name
        )
    )

def create_search_skillset(
        skillset_name,
        index_name,
        azure_openai_endpoint,
        azure_openai_embedding_deployment_id,
        azure_openai_key=None,
        text_split_mode='pages',
        maximum_page_length=2000,
        page_overlap_length=500):
    return SearchIndexerSkillset(
        name=skillset_name,
        skills=[
            SplitSkill(
                name="Text Splitter",
                default_language_code="en",
                text_split_mode=text_split_mode,
                maximum_page_length=maximum_page_length,
                page_overlap_length=page_overlap_length,
                context="/document",
                inputs=[
                    InputFieldMappingEntry(
                        name="text",
                        source="/document/content"
                    )
                ],
                outputs=[
                    OutputFieldMappingEntry(
                        name="textItems",
                        target_name="pages"
                    )
                ]
            ),
            AzureOpenAIEmbeddingSkill(
                name="Embeddings",
                resource_uri=azure_openai_endpoint,
                deployment_id=azure_openai_embedding_deployment_id,
                api_key=azure_openai_key, # Optional if using RBAC authentication
                context="/document/pages/*",
                inputs=[
                    InputFieldMappingEntry(
                        name="text",
                        source="/document/pages/*"
                    )
                ],
                outputs=[
                    OutputFieldMappingEntry(
                        name="embedding",
                        target_name="vector"
                    )
                ]
            )
        ],
        index_projections=SearchIndexerIndexProjections(
            selectors=[
                SearchIndexerIndexProjectionSelector(
                    target_index_name=index_name,
                    parent_key_field_name="parent_id",
                    source_context="/document/pages/*",
                    mappings=[
                        InputFieldMappingEntry(
                            name="chunk",
                            source="/document/pages/*"
                        ),
                        InputFieldMappingEntry(
                            name="vector",
                            source="/document/pages/*/vector"
                        ),
                        InputFieldMappingEntry(
                            name="title",
                            source="/document/metadata_storage_name"
                        )
                    ]
                )
            ],
            parameters=SearchIndexerIndexProjectionsParameters(projection_mode="skipIndexingParentDocuments")
        )
    )

def create_search_indexer(
    indexer_name,
    skillset_name,
    datasource_name,
    index_name):
    return SearchIndexer(
        name=indexer_name,
        data_source_name=datasource_name,
        target_index_name=index_name,
        skillset_name=skillset_name
    )

def get_chunks(search_client):
    results = search_client.search(search_text="*", top=100000, select="chunk_id,chunk")
    chunks = {}
    for result in results:
        id = int(result["chunk_id"].split("_")[3])
        chunks[id] = result["chunk"]
    return [chunks[id] for id in sorted(chunks.keys())]
