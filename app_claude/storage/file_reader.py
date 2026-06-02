from pathlib import Path


class FileReader:

    @staticmethod
    def get_pdf_files(directory):

        return list(
            Path(directory).glob("*.pdf")
        )

    @staticmethod
    def get_text_files(directory):

        return list(
            Path(directory).glob("*.txt")
        )

    @staticmethod
    def read_text(file_path):

        with open(
            file_path,
            "r",
            encoding="utf-8"
        ) as f:

            return f.read()
