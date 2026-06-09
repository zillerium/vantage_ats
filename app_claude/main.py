import argparse

from config import settings
from config.settings import Settings

from services.azure_document_intelligence import AzureDocumentIntelligenceClientWrapper

 
from services.azure_openai import AzureOpenAIService
from services.text_extractor import TextExtractor
from services.job_description_classifier import (
    JobDescriptionClassifier
)

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
        choices=["extract_jd", "extract_product", "jd", "product", "prepare_load", "product_csv", "db_load", "all"],
        help=(
            "Which pipeline to run: "
            "'extract_jd' (PDF→text), "
            "'extract_product' (PDF→text), "
            "'jd' (text→JSON), "
            "'product' (text→JSON), "
            "'product_csv' (JSON→CSV), "
            "'prepare_load' (Concatenate fragments), "
            "'db_load' (CSV→CosmosDB Graph), "
            "'all' (extract and classify in sequence)"
        )
    )

    args = parser.parse_args()

    settings = Settings.load()
    settings.validate()

 


    if args.pipeline in ("extract_jd", "all"):

        print("\n🚀 Starting PDF jd extraction pipeline")

        build_txt_pipeline(settings, settings.jd_pdf_dir, settings.jd_txt_dir, settings.jd_processed_pdf_dir).process_all_pdfs()

    if args.pipeline in ("extract_product", "all"):

        print("\n🚀 Starting PDF product extraction pipeline")

        build_txt_pipeline(settings, settings.product_pdf_dir, settings.product_txt_dir, settings.product_processed_pdf_dir).process_all_pdfs()


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
