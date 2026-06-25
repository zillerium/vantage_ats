from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient


class AzureVectorSearchService:
    """Azure AI Search vector index wrapper for ICO RAG ingestion."""

    def __init__(self, settings):
        self.settings = settings

        print(f"SEARCH_ENDPOINT={settings.azure_search_endpoint}")
        print(f"SEARCH_INDEX={settings.azure_search_index}")
        print(f"SEARCH_KEY_PRESENT={bool(settings.azure_search_admin_key)}")

        if not settings.azure_search_endpoint:
            raise ValueError("Missing AZURE_SEARCH_ENDPOINT")

        if not settings.azure_search_admin_key:
            raise ValueError("Missing AZURE_SEARCH_ADMIN_KEY")

        if not settings.azure_search_index:
            raise ValueError("Missing AZURE_SEARCH_INDEX")

        self.client = SearchClient(
            endpoint=settings.azure_search_endpoint,
            index_name=settings.azure_search_index,
            credential=AzureKeyCredential(settings.azure_search_admin_key)
        )

    def insert_vector_chunk(
        self,
        document_id: str,
        chunk_id: str,
        text_content: str,
        vector: list,
        topic: str = "ico"
    ):
        """
        Upload one text chunk into Azure AI Search.

        This matches the working sample index schema:
        id, text, source, topic, vector
        """

        document = {
            "id": chunk_id,
            "text": text_content,
            "source": document_id,
            "topic": topic,
            "vector": vector
        }

        result = self.client.upload_documents(documents=[document])
        return result