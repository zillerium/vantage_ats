from pathlib import Path


class PdfPipeline:

    def __init__(
        self,
        settings,
        document_service,
        text_extractor,
        file_reader,
        file_writer,
        file_mover
    ):

        self.settings = settings
        self.document_service = document_service
        self.text_extractor = text_extractor
        self.file_reader = file_reader
        self.file_writer = file_writer
        self.file_mover = file_mover

    def process_all_pdfs(self):

        pdf_files = self.file_reader.get_pdf_files(
            self.settings.pdf_input_dir
        )

        print(f"\n📂 Found {len(pdf_files)} PDF files")

        for index, pdf_path in enumerate(pdf_files, 1):

            print("\n" + "=" * 70)
            print(
                f"📄 Processing PDF "
                f"({index}/{len(pdf_files)}): "
                f"{pdf_path.name}"
            )

            self._process_single_pdf(pdf_path)

        print("\n🎉 PDF extraction complete")

    def _process_single_pdf(self, pdf_path):

        try:

            print("🔄 Analysing PDF...")

            result = self.document_service.analyze_pdf(
                pdf_path
            )

            print(
                f"✅ Analysed "
                f"{len(result.pages)} pages"
            )

        except Exception as e:

            print(f"❌ Failed analysing PDF: {e}")
            return

        try:

            text = self.text_extractor.extract(result)

            output_file = (
                Path(self.settings.pdf_output_dir)
                / f"{pdf_path.stem}.txt"
            )

            self.file_writer.write_text(
                output_file,
                text
            )

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
