import shutil
from pathlib import Path


class FileMover:

    @staticmethod
    def move_file(source, destination_dir):

        Path(destination_dir).mkdir(
            parents=True,
            exist_ok=True
        )

        destination = (
            Path(destination_dir) / Path(source).name
        )

        shutil.move(source, destination)

        return destination
