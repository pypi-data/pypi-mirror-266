from filesysteminfo import FileSystemInfo
from fileinfo import FileInfo
import os
import shutil
from pathlib import Path

class DirectoryInfo(FileSystemInfo):
    def __init__(self, path):
        super().__init__(path)

    @property
    def length(self):
        total_size = 0
        for root, dirs, files in os.walk(self._path):
            for name in files:
                filepath = Path(root) / name
                if not filepath.is_symlink():
                    total_size += filepath.stat().st_size
        return total_size

    def create(self):
        self._path.mkdir(parents=True, exist_ok=True)

    def get_files(self, pattern='*'):
        return [FileInfo(child) for child in self._path.glob(pattern) if child.is_file()]

    def get_directories(self, pattern='*'):
        return [DirectoryInfo(child) for child in self._path.glob(pattern) if child.is_dir()]

    def move_to(self, dest):
        destination = Path(dest).resolve()
        shutil.move(self._path, destination)
        self._path = destination