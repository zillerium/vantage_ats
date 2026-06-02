# pipelines/pdf_pipeline.py
from pathlib import Path

class PdfPipeline:

    def __init__(
        self,
        settings,
        document_analyzer,  # Explicit domain-driven name replacing 'document_service'
        text_extractor,
        file_reader,
        file_writer,
        file_mover
    ):
        self.settings = settings
        self.document_analyzer = document_analyzer
        self.text_extractor = text_extractor
        self.file_reader = file_reader
        self.file_writer = file_writer
        self.file_mover = file_mover

    def process_all_pdfs(self):
        pdf_files = self.file_reader.get_pdf_files(self.settings.pdf_input_dir)
        print(f"\n📂 Found {len(pdf_files)} PDF files")

        for index, pdf_path in enumerate(pdf_files, 1):
            print("\n" + "=" * 70)
            print(f"📄 Processing PDF ({index}/{len(pdf_files)}): {pdf_path.name}")
            self._process_single_pdf(pdf_path)

        print("\n🎉 PDF extraction complete")

    def _process_single_pdf(self, pdf_path):
        try:
            print("🔄 Analysing PDF via Azure Document Intelligence...")

            # 1. Read the file into bytes here at the pipeline/storage boundary
            with open(pdf_path, "rb") as f:
                pdf_bytes = f.read()

            # 2. Call the domain-specific method passing the raw data bytes
            result_dict = self.document_analyzer.analyze_job_ad(pdf_bytes)

            # 3. Read safely from the returned dictionary rather than an SDK object
            total_pages = len(result_dict.get("pages", []))
            print(f"✅ Analysed {total_pages} pages")

        except Exception as e:
            print(f"❌ Failed analysing PDF: {e}")
            return

        try:
            # Pass the clean dict payload to your text extractor
            text = self.text_extractor.extract(result_dict)

            output_file = (
                Path(self.settings.pdf_output_dir)
                / f"{pdf_path.stem}.txt"
            )

            self.file_writer.write_text(output_file, text)
            print(f"✅ Saved text: {output_file}")

        except Exception as e:
            print(f"❌ Failed extracting text: {e}")
            return

        try:
            destination = self.file_mover.move_file(
                pdf_path,
                self.settings.pdf_archive_dir
            )
            print(f"📦 Archived PDF: {destination}")

        except Exception as e:
            print(f"❌ Failed archiving PDF: {e}")