from dataclasses import dataclass
from dotenv import load_dotenv
import os

load_dotenv()


@dataclass
class Settings:

    # Azure Document Intelligence (PDF → text)
    azure_doc_endpoint: str
    azure_doc_key: str

    # Azure OpenAI (text → JSON)
    azure_openai_endpoint: str
    azure_openai_key: str
    azure_openai_model: str

    # PDF pipeline directories
    pdf_input_dir: str
    pdf_output_dir: str
    pdf_archive_dir: str

    # JD classifier pipeline directories
    jd_input_dir: str
    jd_output_dir: str

    @classmethod
    def load(cls):

        return cls(
            azure_doc_endpoint=os.getenv(
                "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT"
            ),
            azure_doc_key=os.getenv(
                "AZURE_DOCUMENT_INTELLIGENCE_KEY"
            ),
            azure_openai_endpoint=os.getenv(
                "AZURE_MODEL_EUROPE_ENDPOINT"
            ),
            azure_openai_key=os.getenv(
                "AZURE_EUROPE_KEY"
            ),
            azure_openai_model=os.getenv(
                "AZURE_OPENAI_MODEL",
                "gpt-5.4-mini"
            ),
         pdf_input_dir=os.getenv(
                "PDF_INPUT_DIR"
            ),
            pdf_output_dir=os.getenv(
                "PDF_OUTPUT_DIR"
            ),
            pdf_archive_dir=os.getenv(
                "PDF_ARCHIVE_DIR"
            ),
            jd_input_dir=os.getenv(
                "JD_INPUT_DIR"
            ),
            jd_output_dir=os.getenv(
                "JD_OUTPUT_DIR"
            ),
  
        )

    def validate(self):
        """Raise ValueError for any missing required credentials."""

        required = {
            "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT": self.azure_doc_endpoint,
            "AZURE_DOCUMENT_INTELLIGENCE_KEY": self.azure_doc_key,
            "AZURE_MODEL_EUROPE_ENDPOINT": self.azure_openai_endpoint,
            "AZURE_EUROPE_KEY": self.azure_openai_key,
        }

        missing = [
            name for name, value in required.items()
            if not value
        ]

        if missing:
            raise ValueError(
                f"Missing required .env variables: "
                f"{', '.join(missing)}"
            )

        if not self.azure_doc_endpoint.startswith("https://"):
            raise ValueError(
                "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT "
                "must start with https://"
            )
