from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient

class AzureVectorSearchService:
    """Standard client wrapper for Azure's dedicated RAG vector search index service."""

    def __init__(self, settings):
        self.settings = settings
        # Seamlessly initializes using your existing central settings configuration object
        self.client = SearchClient(
            endpoint=settings.azure_openai_endpoint,
            index_name="ico-rag-index",
            credential=AzureKeyCredential(settings.azure_openai_key)
        )

    def insert_vector_chunk(self, document_id: str, chunk_id: str, text_content: str, vector: list):
        """Native target execution context payload upload to Azure Vector Index."""
        document = {
            "id": chunk_id,
            "document_id": document_id,
            "content": text_content,
            "content_vector": vector
        }
        self.client.upload_documents(documents=[document])