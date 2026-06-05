import argparse

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

from pipelines.pdf_pipeline import PdfPipeline
from pipelines.jd_pipeline import JDPipeline

# Update your import to reflect the domain wrapper
from services.azure_text_classifer import AzureTextClassifierWrapper
from services.job_description_classifier import JobDescriptionClassifier
from services.reddit_product_classifer import RedditProductClassifier
 
 

def build_pdf_pipeline(settings):

    # Clarify the variable name and use the new wrapper class
    document_analyzer = AzureDocumentIntelligenceClientWrapper(
        endpoint=settings.azure_doc_endpoint,
        key=settings.azure_doc_key
    )

    return PdfPipeline(
        settings=settings,
        document_analyzer=document_analyzer,
        text_extractor=TextExtractor(),
        file_reader=FileReader(),
        file_writer=FileWriter(),
        file_mover=FileMover()
    )


 
 
def build_jd_pipeline(settings, text_analyzer):


    # 2. Inject it cleanly into your existing classifier manager
    classifier = JobDescriptionClassifier(
        openai_service=text_analyzer, # Backward compatible parameter injection
        model=settings.azure_openai_model
    )

    return JDPipeline(
        settings=settings,
        classifier=classifier,
        file_reader=FileReader(),
        file_writer=FileWriter()
    )

 


 
 
def build_product_pipeline(settings, text_analyzer):


    # 2. Inject it cleanly into your existing classifier manager
    classifier = RedditProductClassifier(
        openai_service=text_analyzer, # Backward compatible parameter injection
        model=settings.azure_openai_model
    )

    return JDPipeline(
        settings=settings,
        classifier=classifier,
        file_reader=FileReader(),
        file_writer=FileWriter()
    )


def main():

    parser = argparse.ArgumentParser(
        description="VantageCV pipeline runner"
    )

    parser.add_argument(
        "pipeline",
        choices=["extract", "classify", "product", "all"],
        help=(
            "Which pipeline to run: "
            "'extract' (PDF→text), "
            "'classify' (text→JSON), "
            "'all' (both in sequence)"
        )
    )

    args = parser.parse_args()

    settings = Settings.load()
    settings.validate()

    if args.pipeline in ("extract", "all"):

        print("\n🚀 Starting PDF extraction pipeline")

        build_pdf_pipeline(settings).process_all_pdfs()

    if args.pipeline in ("classify", "all"):

        print("\n🚀 Starting JD classification pipeline")

        # 1. Clear variable name indicating domain purpose
        text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )

        build_jd_pipeline(settings, text_analyzer).process_all_files()

    if args.pipeline in ("product", "all"):

        print("\n🚀 Starting product classification pipeline")

        # 1. Clear variable name indicating domain purpose
        text_analyzer = AzureTextClassifierWrapper(
            endpoint=settings.azure_openai_endpoint,
            api_key=settings.azure_openai_key
        )

        build_product_pipeline(settings, text_analyzer).process_all_files()


if __name__ == "__main__":
    main()
