import unittest
from pathlib import Path
from tempfile import TemporaryDirectory
from fileinfo import FileInfo

class TestFileInfo(unittest.TestCase):

    def test_file_info(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file_path = Path(tmpdir, "test.txt")
            tmp_file_path.touch()
            file_info = FileInfo(str(tmp_file_path))

            self.assertEqual(file_info.length, 0)  # Empty file has length 0
            self.assertFalse(file_info.is_read_only)  # Newly created file is not read-only
            self.assertEqual(file_info.extension, '.txt')
            
            # Write to file and test length update
            with file_info.create_text() as f:
                f.write("Hello")
            self.assertEqual(file_info.length, 5)

            # Test read from file
            with file_info.open_text() as f:
                content = f.read()
                self.assertEqual(content, "Hello")

            # Copy file and test existence
            copy_path = Path(tmpdir, "copy.txt")
            file_info.copy_to(copy_path)
            self.assertTrue(copy_path.exists())

            # Move file and test new location
            move_path = Path(tmpdir, "moved.txt")
            file_info.move_to(move_path)
            self.assertTrue(move_path.exists())
            # Adjusted assertion
            self.assertEqual(Path(file_info.full_name).resolve(), move_path.resolve())

            # Clean up
            file_info.delete()
            self.assertFalse(move_path.exists())

    def test_directory_and_directory_name_properties(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file_path = Path(tmpdir, "test_file.txt")
            tmp_file_path.touch()
            file_info = FileInfo(str(tmp_file_path))

            # Ensure both paths are resolved before comparison to account for symlink resolution
            self.assertEqual(file_info.directory.resolve(), tmp_file_path.parent.resolve())
            self.assertEqual(file_info.directory_name, str(tmp_file_path.parent.resolve()))

    def test_read_only_property(self):
        with TemporaryDirectory() as tmpdir:
            tmp_file_path = Path(tmpdir) / "test_file.txt"
            tmp_file_path.touch()
            file_info = FileInfo(str(tmp_file_path))

            file_info.is_read_only = True
            self.assertTrue(file_info.is_read_only)

            file_info.is_read_only = False
            self.assertFalse(file_info.is_read_only)

    def test_copy_to_overwrite(self):
        with TemporaryDirectory() as tmpdir:
            source_path = Path(tmpdir) / "source.txt"
            dest_path = Path(tmpdir) / "dest.txt"
            source_path.touch()
            dest_path.touch()  # Ensure destination file exists

            source_file = FileInfo(str(source_path))

            # Expecting FileExistsError due to existing destination and overwrite=False
            with self.assertRaises(FileExistsError):
                source_file.copy_to(str(dest_path), overwrite=False)

            # Test successful copy with overwrite=True
            source_file.copy_to(str(dest_path), overwrite=True)
            self.assertTrue(dest_path.exists())

if __name__ == '__main__':
    unittest.main()
