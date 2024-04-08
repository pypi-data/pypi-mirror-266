import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from directoryinfo import DirectoryInfo

class TestDirectoryInfo(unittest.TestCase):

    def test_directory_info(self):
        with TemporaryDirectory() as tmpdir:
            # Create a subdirectory and test creation
            sub_dir_path = Path(tmpdir, "subdir")
            dir_info = DirectoryInfo(str(sub_dir_path))
            dir_info.create()
            self.assertTrue(dir_info.exists)

            # Test length with an empty directory
            self.assertEqual(dir_info.length, 0)

            # Add a file to the directory and test length update
            file_path = sub_dir_path / "test.txt"
            file_path.touch()
            file_path.write_text("Hello")
            self.assertEqual(dir_info.length, 5)

            # Test get_files and get_directories
            self.assertEqual(len(dir_info.get_files()), 1)
            self.assertEqual(len(dir_info.get_directories()), 0)

            # Clean up
            dir_info.delete()
            self.assertFalse(dir_info.exists)

    def test_move_directory(self):
        with TemporaryDirectory() as tmpdir:
            source_dir = Path(tmpdir) / "source_dir"
            dest_dir_path = Path(tmpdir) / "dest_dir"
            source_dir.mkdir()
            dir_info = DirectoryInfo(str(source_dir))

            dir_info.move_to(str(dest_dir_path))
            self.assertFalse(source_dir.exists())  # Source should no longer exist
            self.assertTrue(dest_dir_path.exists())  # Destination should now exist
            self.assertEqual(dir_info.full_name, str(dest_dir_path.resolve()))  # Path should update

if __name__ == '__main__':
    unittest.main()
