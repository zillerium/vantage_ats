# pipelines/ico_rag_query_pipeline.py
from services.azure_rag_query_service import AzureRagQueryService

class ICORagQueryPipeline:
    def __init__(self, settings, vector_store, openai_service):
        self.query_service = AzureRagQueryService(
            settings=settings,
            vector_store=vector_store,
            openai_service=openai_service
        )

    def run_query(self, query_text: str):
        """Entry point called by main.py to handle the search execution flow."""
        self.query_service.query(query_text)