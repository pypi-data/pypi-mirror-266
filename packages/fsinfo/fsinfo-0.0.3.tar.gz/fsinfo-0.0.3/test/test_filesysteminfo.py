import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from filesysteminfo import FileSystemInfo
from datetime import datetime
from unittest.mock import patch, MagicMock
from datetime import datetime, timezone

class TestFileSystemInfo(unittest.TestCase):

    def test_file_system_info(self):
        with TemporaryDirectory() as tmpdir:
            # Test creation_time, exists, full_name, last_access_time, last_write_time, and name properties
            tmp_file_path = Path(tmpdir, "test.txt")
            tmp_file_path.touch()
            fs_info = FileSystemInfo(tmp_file_path)
            
            self.assertTrue(fs_info.exists)
            self.assertEqual(fs_info.name, "test.txt")
            self.assertTrue(isinstance(fs_info.creation_time, datetime))
            self.assertTrue(isinstance(fs_info.last_access_time, datetime))
            self.assertTrue(isinstance(fs_info.last_write_time, datetime))
            self.assertEqual(Path(fs_info.full_name).resolve(), tmp_file_path.resolve())
            
            # Test delete method
            fs_info.delete()
            self.assertFalse(fs_info.exists)
    
    @patch.object(Path, 'stat')
    def test_creation_time_with_st_birthtime(self, mock_stat):
        # Simulate environment where st_birthtime is available
        mock_stat.return_value = MagicMock(st_birthtime=1633030800, st_ctime=1633030800)
        fs_info = FileSystemInfo('some/path')

        expected_time = datetime.fromtimestamp(1633030800, tz=timezone.utc)
        self.assertEqual(fs_info.creation_time, expected_time)

    @patch.object(Path, 'stat')
    def test_creation_time_fallback_to_st_ctime(self, mock_stat):
        # Simulate environment where st_birthtime is not available
        mock_stat.return_value = MagicMock(st_ctime=1633030800)
        # Remove the attribute to simulate an AttributeError
        delattr(mock_stat.return_value, 'st_birthtime')
        
        fs_info = FileSystemInfo('some/path')

        expected_time = datetime.fromtimestamp(1633030800, tz=timezone.utc)
        self.assertEqual(fs_info.creation_time, expected_time)

if __name__ == '__main__':
    unittest.main()
