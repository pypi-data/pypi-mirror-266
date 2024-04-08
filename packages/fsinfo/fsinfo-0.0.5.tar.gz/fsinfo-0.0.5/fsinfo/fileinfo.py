from filesysteminfo import FileSystemInfo
from pathlib import Path
import shutil

class FileInfo(FileSystemInfo):
    def __init__(self, path):
        super().__init__(path)

    @property
    def directory(self):
        return self._path.parent
    
    @property
    def directory_name(self):
        return str(self.directory)

    @property
    def length(self):
        return self._path.stat().st_size if self.exists else 0

    @property
    def is_read_only(self):
        return not self._path.stat().st_mode & 0o222
    
    @property
    def extension(self):
        return self._path.suffix

    @is_read_only.setter
    def is_read_only(self, value):
        mode = self._path.stat().st_mode
        self._path.chmod(mode & ~0o222 if value else mode | 0o222)

    def create_text(self):
        return self._path.open(mode='w+', encoding='utf-8')

    def open_text(self):
        return self._path.open(mode='r', encoding='utf-8')

    def copy_to(self, dest, overwrite=False):
        destination = Path(dest).resolve()
        if destination.exists() and not overwrite:
            raise FileExistsError(f"File {dest} already exists and overwrite is False.")
        return FileInfo(shutil.copy2(self._path, destination))

    def move_to(self, dest):
        destination = Path(dest).resolve()
        shutil.move(self._path, destination)
        self._path = destination
