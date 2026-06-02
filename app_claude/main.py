import argparse

from config.settings import Settings

from services.azure_document_intelligence import (
    AzureDocumentIntelligenceService
)
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


def build_pdf_pipeline(settings):

    document_service = AzureDocumentIntelligenceService(
        endpoint=settings.azure_doc_endpoint,
        key=settings.azure_doc_key
    )

    return PdfPipeline(
        settings=settings,
        document_service=document_service,
        text_extractor=TextExtractor(),
        file_reader=FileReader(),
        file_writer=FileWriter(),
        file_mover=FileMover()
    )


def build_jd_pipeline(settings):

    openai_service = AzureOpenAIService(
        endpoint=settings.azure_openai_endpoint,
        api_key=settings.azure_openai_key
    )

    classifier = JobDescriptionClassifier(
        openai_service=openai_service,
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
        choices=["extract", "classify", "all"],
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

        build_jd_pipeline(settings).process_all_files()


if __name__ == "__main__":
    main()
