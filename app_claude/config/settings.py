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

    # ICO Pipeline Directories
    ico_pdf_dir: str
    ico_txt_dir: str
    ico_json_dir: str
    ico_processed_pdf_dir: str
    ico_processed_txt_dir: str

    # ICO Pipeline Directories
    ico_pdf_dir: str
    ico_txt_dir: str
    ico_json_dir: str
    ico_processed_pdf_dir: str
    ico_processed_txt_dir: str

    # JD Pipeline Directories
    jd_pdf_dir: str
    jd_txt_dir: str
    jd_json_dir: str
    jd_processed_pdf_dir: str
    jd_processed_txt_dir: str
    product_jd_json_dir: str
    jd_processed_json_dir: str

    # Product Pipeline Directories
    product_pdf_dir: str
    product_txt_dir: str
    product_json_dir: str
    product_processed_txt_dir: str
    product_processed_pdf_dir: str
    product_jd_processed_json_dir: str

    database_load_csv_dir: str
    database_product_csv_dir: str                   # Added field assignment
    database_product_processed_csv_dir: str         # Added field assignment
    database_load_csv_file_name: str                 # Added field assignment
    database_product_csv_file_name: str

    # Database Pipeline Configs
   
    cosmos_gremlin_endpoint: str
    cosmos_key: str
    cosmos_database_id: str
    cosmos_graph_id: str
  
    product_processed_json_dir: str  # Added to track processed raw JSON files

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
            # JD Pipeline
            jd_pdf_dir=os.getenv(
                "JD_PDF_DIR", 
                "../../jd/jd-pdf"
            ),
            jd_txt_dir=os.getenv(
                "JD_TXT_DIR", 
                "../../jd/jd-txt"
            ),
            jd_json_dir=os.getenv(
                "JD_JSON_DIR", 
                "../../jd/jd-json"
            ),
            jd_processed_txt_dir=os.getenv(
                "JD_PROCESSED_TXT_DIR", 
                "../../jd/jd-processed-txt"
            ),
            jd_processed_pdf_dir=os.getenv(
                "JD_PROCESSED_PDF_DIR", 
                "../../jd/jd-processed-pdf"
            ),
            # ICO Pipeline
            ico_pdf_dir=os.getenv(
                "ICO_PDF_DIR", 
                "../../ico/ico-pdf"
            ),
            ico_txt_dir=os.getenv(
                "ICO_TXT_DIR", 
                "../../ico/ico-txt"
            ),
            ico_json_dir=os.getenv(
                "ICO_JSON_DIR", 
                "../../ico/ico-json"
            ),
            ico_processed_pdf_dir=os.getenv(
                "ICO_PROCESSED_PDF_DIR", 
                "../../ico/ico-processed-pdf"
            ),
            ico_processed_txt_dir=os.getenv(
                "ICO_PROCESSED_TXT_DIR", 
                "../../ico/ico-processed-txt"
            ),
            # Product Pipeline
            product_pdf_dir=os.getenv(
                "PRODUCT_PDF_DIR", 
                "../../product/product-pdf"
            ),
            product_txt_dir=os.getenv(
                "PRODUCT_TXT_DIR", 
                "../../product/product-txt"
            ),
            product_json_dir=os.getenv(
                "PRODUCT_JSON_DIR", 
                "../../product/product-json"
            ),
            product_processed_txt_dir=os.getenv(
                "PRODUCT_PROCESSED_TXT_DIR", 
                "../../product/product-processed-txt"
            ),
            product_processed_pdf_dir=os.getenv(
                "PRODUCT_PROCESSED_PDF_DIR", 
                "../../product/product-processed-pdf"
            ),
            product_processed_json_dir=os.getenv(
                "PRODUCT_PROCESSED_JSON_DIR", 
                "../../product/product-processed-json"
            ),
           # Database Pipeline

            jd_processed_json_dir=os.getenv("JD_PROCESSED_JSON_DIR", "../../jd/jd-processed-json"),
            product_jd_json_dir=os.getenv("PRODUCT_JD_JSON_DIR", "../../jd-product/jd-product-json"),
            product_jd_processed_json_dir=os.getenv("PRODUCT_JD_PROCESSED_JSON_DIR", "../../jd-product/jd-product-processed-json"),   

            database_load_csv_dir=os.getenv("DATABASE_LOAD_CSV_DIR", "../../database/csv_load"),
            database_product_processed_csv_dir=os.getenv("DATABASE_PRODUCT_PROCESSED_CSV_DIR", "../../database/csv_product-processed"),  # ← ADD THIS
            database_product_csv_dir=os.getenv("DATABASE_PRODUCT_CSV_DIR", "../../database/csvproduct"),
            database_load_csv_file_name=os.getenv("DATABASE_LOAD_CSV_FILE_NAME", "dataload.csv"),
            database_product_csv_file_name=os.getenv("DATABASE_PRODUCT_CSV_FILE_NAME", "productload.csv"),
            cosmos_gremlin_endpoint=os.getenv("AZURE_COSMOSDB_PRODUCT_PRIMARY_CONNECTION_GREMLIN_ENDPOINT"),
            cosmos_key=os.getenv("AZURE_COSMOSDB_PRODUCT_PRIMARY_KEY"),
            cosmos_database_id=os.getenv("AZURE_COSMOSDB_DATABASE_ID", "productdbid"),
            cosmos_graph_id=os.getenv("AZURE_COSMOSDB_GRAPH_ID", "allproducts"),
             
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

        if not self.azure_doc_endpoint or not self.azure_doc_endpoint.startswith("https://"):
            raise ValueError(
                "AZURE_DOCUMENT_INTELLIGENCE_ENDPOINT "
                "must start with https://"
            )