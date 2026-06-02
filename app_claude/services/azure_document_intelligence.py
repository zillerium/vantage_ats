from azure.ai.documentintelligence import DocumentIntelligenceClient
from azure.core.credentials import AzureKeyCredential


class AzureDocumentIntelligenceService:

    def __init__(self, endpoint, key):

        self.client = DocumentIntelligenceClient(
            endpoint=endpoint,
            credential=AzureKeyCredential(key)
        )

    def analyze_pdf(self, pdf_path):

        with open(pdf_path, "rb") as f:

            poller = self.client.begin_analyze_document(
                "prebuilt-layout",
                f
            )

            return poller.result()
