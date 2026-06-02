from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential

class AzureDocumentIntelligenceClientWrapper:
    """
    A domain-specific wrapper around the Azure Document Intelligence SDK.
    Provides clear intent for document analysis within the ATS workflow.
    """
    def __init__(self, endpoint: str, key: str):
        self.document_intelligence_client = DocumentIntelligenceClient(
            endpoint=endpoint, 
            credential=AzureKeyCredential(key)
        )

    def analyze_job_ad(self, document_bytes: bytes) -> dict:
        """
        Uses Azure's prebuilt layout model to analyze and extract structural data from a job advertisement.
        Returns a standard Python dictionary for downstream processing.
        """
        # Pass the bytes stream directly to 'body' parameter to avoid object extraction bugs
        poller = self.document_intelligence_client.begin_analyze_document(
            model_id="prebuilt-layout", 
            body=document_bytes,
            content_type="application/octet-stream" # Declares we are sending binary data directly
        )
        
        # Block until processing is complete
        sdk_result = poller.result()
        
        # Convert to a dictionary so the rest of the app isn't coupled to Azure SDK types
        return sdk_result.as_dict()