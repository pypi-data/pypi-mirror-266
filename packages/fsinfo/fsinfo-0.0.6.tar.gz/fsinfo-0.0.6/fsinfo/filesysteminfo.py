from pathlib import Path
from datetime import datetime, timezone

class FileSystemInfo:
    def __init__(self, path):
        self._path = Path(path).resolve()
    
    @property
    def creation_time(self):
        try:
            # Try to use st_birthtime for creation time if available (Python 3.10+)
            return datetime.fromtimestamp(self._path.stat().st_birthtime, tz=timezone.utc)
        except AttributeError:
            # Fall back to st_ctime for Unix-like systems or if st_birthtime is not available
            return datetime.fromtimestamp(self._path.stat().st_ctime, tz=timezone.utc)

    @property
    def exists(self):
        return self._path.exists()

    @property
    def full_name(self):
        return str(self._path)

    @property
    def last_access_time(self):
        return datetime.fromtimestamp(self._path.stat().st_atime, tz=timezone.utc)

    @property
    def last_write_time(self):
        return datetime.fromtimestamp(self._path.stat().st_mtime, tz=timezone.utc)

    @property
    def name(self):
        return self._path.name

    def delete(self):
        if self._path.is_dir():
            for child in self._path.iterdir():
                FileSystemInfo(child).delete()
            self._path.rmdir()
        else:
            self._path.unlink()