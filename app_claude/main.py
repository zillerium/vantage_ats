import argparse

from config import settings
from config.settings import Settings

from services.azure_document_intelligence import AzureDocumentIntelligenceClientWrapper
from services.azure_vector_search_service import AzureVectorSearchService 
 
from services.azure_openai import AzureOpenAIService
from services.text_extractor import TextExtractor
from services.job_description_classifier import (
    JobDescriptionClassifier
)

from pipelines.ico_rag_query_pipeline import ICORagQueryPipeline
from services.ico_classifier import ICOClassifier
from pipelines.ico_rag_pipeline import ICORagPipeline

from storage.file_reader import FileReader
from storage.file_writer import FileWriter
from storage.file_mover import FileMover

from pipelines.pdf2txt_pipeline import Pdf2TxtPipeline
from pipelines.txt2json_pipeline import Txt2JsonPipeline

# Update your import to reflect the domain wrapper
from services.azure_text_classifer import AzureTextClassifierWrapper
from services.job_description_classifier import JobDescriptionClassifier
from services.reddit_product_classifer import RedditProductClassifier
 
from pipelines.db_product_load_pipeline import DbProductLoadPipeline  # Added new pipeline import
from pipelines.json2csv_pipeline import Json2CsvPipeline  # Added new pipeline import
from pipelines.prepare_db_product_load_pipeline import PrepareDbProductLoadPipeline

from services.jd_product_classifier import JobDescriptionProductClassifier
from pipelines.jd_product_pipeline import JobDescriptionProductPipeline

def build_prepare_load_pipeline(settings):
    """Instantiates the database load pre-aggregation worker layer pipeline context."""
    return PrepareDbProductLoadPipeline(
        settings=settings,
        file_reader=FileReader(),
        file_mover=FileMover(),
        product_csv_dir=settings.database_product_csv_dir,
        load_csv_dir=settings.database_load_csv_dir,
        load_csv_file_name=settings.database_load_csv_file_name,
        processed_csv_dir=settings.database_product_processed_csv_dir
    )

def build_txt_pipeline(settings,in_directory, out_directory, in_processed_dir):

    # Clarify the variable name and use the new wrapper class
    document_analyzer = AzureDocumentIntelligenceClientWrapper(
        endpoint=settings.azure_doc_endpoint,
        key=settings.azure_doc_key
    )

    return Pdf2TxtPipeline(
        settings=settings,
        document_analyzer=document_analyzer,
        text_extractor=TextExtractor(),
        file_reader=FileReader(),
        file_writer=FileWriter(),
        file_mover=FileMover(),
        pdf_input_dir=in_directory,
        txt_output_dir=out_directory,
        pdf_processed_dir=in_processed_dir
    )

 
 
 
def build_jd_pipeline(settings, text_analyzer):


    # 2. Inject it cleanly into your existing classifier manager
    classifier = JobDescriptionClassifier(
        openai_service=text_analyzer, # Backward compatible parameter injection
        model=settings.azure_openai_model
    )

    return Txt2JsonPipeline(
        settings=settings,
        classifier=classifier,
        file_reader=FileReader(),
        file_writer=FileWriter(),        
        file_mover=FileMover(),
        text_input_dir=settings.jd_txt_dir,
        json_output_dir=settings.jd_json_dir,
        text_processed_dir=settings.jd_processed_txt_dir
    )

 
def build_product_csv_pipeline(settings):
    """Instantiates the JSON to CSV conversion pipeline container."""
    return Json2CsvPipeline(
        settings=settings,
        file_reader=FileReader(),
        file_mover=FileMover(),
        json_input_dir=settings.product_json_dir,
        csv_output_dir=settings.database_product_csv_dir,
        json_processed_dir=settings.product_processed_json_dir
    )

def build_product_jd_pipeline(settings, text_analyzer):
    """Instantiates the pipeline that extracts products and classifications from JD JSONs."""
    classifier = JobDescriptionProductClassifier(
        openai_service=text_analyzer,
        model=settings.azure_openai_model
    )

    return JobDescriptionProductPipeline(
        settings=settings,
        classifier=classifier,
        file_reader=FileReader(),
        file_writer=FileWriter(),
        file_mover=FileMover(),
        json_input_dir=settings.jd_json_dir,
        json_output_dir=settings.product_jd_json_dir,
        json_processed_dir=settings.jd_processed_json_dir
    )


def build_ico_pipeline(settings, text_analyzer, in_directory, in_processed_dir):

    print(f"SEARCH_ENDPOINT={settings.azure_search_endpoint}")
    print(f"SEARCH_INDEX={settings.azure_search_index}")
    print(f"SEARCH_KEY_PRESENT={bool(settings.azure_search_admin_key)}")
    print(f"EMBEDDING_MODEL={settings.azure_openai_embedding_model}")

    return ICORagPipeline(
        settings=settings,
        vector_store=AzureVectorSearchService(settings=settings),
        openai_service=text_analyzer,
        file_reader=FileReader(),
        file_mover=FileMover(),
        txt_input_dir=in_directory,
        txt_processed_dir=in_processed_dir
    )

def build_ico_rag_query_pipeline(settings, text_analyzer):
    """Instantiates a completely new isolated pipeline context for live queries."""
    return ICORagQueryPipeline(
        settings=settings,
        vector_store=AzureVectorSearchService(settings=settings),
        openai_service=text_analyzer
    )  

def build_product_pipeline(settings, text_analyzer):


    # 2. Inject it cleanly into your existing classifier manager
    classifier = RedditProductClassifier(
        openai_service=text_analyzer, # Backward compatible parameter injection
        model=settings.azure_openai_model
    )

    return Txt2JsonPipeline(
        settings=settings,
        classifier=classifier,
        file_reader=FileReader(),
        file_writer=FileWriter(),
        file_mover=FileMover(),
        text_input_dir=settings.product_txt_dir,
        json_output_dir=settings.product_json_dir,
        text_processed_dir=settings.product_processed_txt_dir
    )

# 2. Add structural instantiation binding factory matching code standards
def build_db_load_pipeline(settings):
    """Instantiates the database processing pipeline container."""
    return DbProductLoadPipeline(settings=settings)

def main():

    parser = argparse.ArgumentParser(
        description="VantageCV pipeline runner"
    )

    parser.add_argument(
        "pipeline",
        choices=["extract_jd", "extract_product", "rag","extract_ico", "jd", "product", "prepare_load", "ico", "create_product_jd", "product_csv", "db_load", "all"],
        help=(
            "Which pipeline to run: "
            "'extract_jd' (PDF→text), "
            "'extract_product' (PDF→text), "
            "'rag' (RAG query), "
            "'extract_ico' (PDF→text), "
            "'jd' (text→JSON), "    
            "'product' (text→JSON), "
            "'product_csv' (JSON→CSV), "
            "'create_product_jd' (Extract product info from JD JSONs), "
            "'prepare_load' (Concatenate fragments), "
            "'db_load' (CSV→CosmosDB Graph), "
            "ico' (Generate ICO), "
            "'all' (extract and classify in sequence)"
        )
    )

    parser.add_argument(
        "query_text",
        nargs="?",
        default=None,
        help="The question text string required when running the 'rag' execution pipeline loop."
    )



    args = parser.parse_args()

    settings = Settings.load()
    settings.validate()

    if args.pipeline in ("create_product_jd", "all"):
        print("\n🚀 Starting Job Description Product Extraction Pipeline")

        text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )

        build_product_jd_pipeline(settings, text_analyzer).process_all_files()


  
    # 🎯 NEW COMPLETELY ADDITIVE PATHWAY — ZERO OLD CODE IMPACTED
    if args.pipeline == "rag":
        if not args.query_text:
            print("\n❌ Error: The 'rag' command choice requires a query string parameter.")
            sys.exit(1)

        rag_text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )
        
        build_ico_rag_query_pipeline(settings, rag_text_analyzer).run_query(args.query_text)
        return  # Exits immediately! Old code below is never reached or evaluated.
            
      

  
    if args.pipeline in ("extract_jd", "all"):

        print("\n🚀 Starting PDF jd extraction pipeline")

        build_txt_pipeline(settings, settings.jd_pdf_dir, settings.jd_txt_dir, settings.jd_processed_pdf_dir).process_all_pdfs()

    if args.pipeline in ("extract_product", "all"):

        print("\n🚀 Starting PDF product extraction pipeline")

        build_txt_pipeline(settings, settings.product_pdf_dir, settings.product_txt_dir, settings.product_processed_pdf_dir).process_all_pdfs()

    if args.pipeline == "extract_ico":
        print("\n🚀 Starting PDF ico extraction pipeline")

        # Following your exact structural pattern:
        build_txt_pipeline(
            settings, 
            settings.ico_pdf_dir, 
            settings.ico_txt_dir, 
            settings.ico_processed_pdf_dir
        ).process_all_pdfs()  
 
    if args.pipeline in ("jd", "all"):

        print("\n🚀 Starting JD classification pipeline")

        # 1. Clear variable name indicating domain purpose
        text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )

        build_jd_pipeline(settings, text_analyzer).process_all_files()

    if args.pipeline in ("product", "all"):

        # this logic will process reddit product reviews from text → JSON using the same AzureTextClassifierWrapper and a new RedditProductClassifier manager class that you would create following the pattern of JobDescriptionClassifier
        print("\n🚀 Starting product classification pipeline")

        # 1. Clear variable name indicating domain purpose
        text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )

        build_product_pipeline(settings, text_analyzer).process_all_files()

    # Runtime check routing execution block to transform JSON files into graph CSV variants
    if args.pipeline in ("product_csv", "all"):
        print("\n🚀 Starting JSON to CSV Transformation pipeline")
        build_product_csv_pipeline(settings).process_all_files()

    
    if args.pipeline in ("ico", "all"):
        print("\n🚀 Starting ICO Data Protection Compliance Pipeline")

        text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )

        build_ico_pipeline(
            settings, 
            text_analyzer,
            settings.ico_txt_dir,
            settings.ico_processed_txt_dir
        ).process_all_files()

    # Runtime block interception triggering our flat compilation execution layer
    if args.pipeline in ("prepare_load", "all"):
        print("\n🚀 Starting DB Data Integration and Merge Preparation Pipeline Step")
        build_prepare_load_pipeline(settings).process_preparation() 

        # Runtime check routing execution block to trigger migration class
    if args.pipeline in ("db_load", "all"):
        print("\n🚀 Starting Graph Database loading pipeline")
        build_db_load_pipeline(settings).process_load()


if __name__ == "__main__":
    main()
