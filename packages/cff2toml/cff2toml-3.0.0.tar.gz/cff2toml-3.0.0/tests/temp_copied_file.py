import tempfile
import shutil
import os


class TempCopiedFile:

    def __init__(self, source_file_path: str):
        self.source_file_path = source_file_path

    def __enter__(self):
        self.tmp = tempfile.NamedTemporaryFile(delete=False)
        shutil.copy2(src=self.source_file_path, dst=self.tmp.name)
        return self

    def __exit__(self, *args):
        os.remove(path=self.tmp.name)

    @property
    def file_path(self) -> str:
        if self.tmp.closed:
            return ''
        return self.tmp.name
