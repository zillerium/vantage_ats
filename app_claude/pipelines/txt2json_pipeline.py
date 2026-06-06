from pathlib import Path


class Txt2JsonPipeline:

    def __init__(
        self,
        settings,
        classifier,
        file_reader,
        file_writer,
        file_mover,  # Added to support file archiving operations
        text_input_dir,
        json_output_dir,
        text_processed_dir
    ):

        self.settings = settings
        self.classifier = classifier
        self.file_reader = file_reader
        self.file_writer = file_writer
        self.file_mover = file_mover
        self.text_input_dir = text_input_dir
        self.json_output_dir = json_output_dir
        self.text_processed_dir = text_processed_dir

    def process_all_files(self):

        txt_files = self.file_reader.get_text_files(
            self.text_input_dir
        )

        print(f"\n📂 Found {len(txt_files)} text files")

        for index, txt_file in enumerate(txt_files, 1):

            print("\n" + "=" * 70)
            print(
                f"📄 Processing file "
                f"({index}/{len(txt_files)}): "
                f"{txt_file.name}"
            )

            self._process_single_file(txt_file)

        print("\n🎉 Classification complete")

    def _process_single_file(self, txt_file):

        try:

            text = self.file_reader.read_text(txt_file)

            print(f"✅ Loaded {len(text):,} chars")

        except Exception as e:

            print(f"❌ Failed reading file: {e}")
            return

        try:

            print("🤖 Running classification...")

            data = self.classifier.classify(text)

            print("✅ Classification complete")

        except Exception as e:

            print(f"❌ Classification failed: {e}")
            return

        try:

            output_file = (
                Path(self.json_output_dir)
                / f"{txt_file.stem}.json"
            )

            self.file_writer.write_json(
                output_file,
                data
            )

            print(f"✅ Saved JSON: {output_file}")

        except Exception as e:

            print(f"❌ Failed saving JSON: {e}")
            return  # Added return to prevent archiving if writing JSON fails

        # 1. Archive the text file after a completely successful pipeline pass
        try:
            destination = self.file_mover.move_file(
                txt_file,
                self.text_processed_dir
            )
            print(f"📦 Archived Text: {destination}")

        except Exception as e:
            print(f"❌ Failed archiving Text: {e}")