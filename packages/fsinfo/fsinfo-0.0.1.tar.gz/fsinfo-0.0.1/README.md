# fsinfo

**fsinfo** is a Python library providing a high-level abstraction for working with filesystem paths, files, and directories in a cross-platform way. It simplifies file system operations like querying file attributes, manipulating directories, and handling files across Linux, macOS, and Windows.

## Features

- **FileSystemInfo**: A base class for handling common file system information retrieval such as creation, modification, and access times.
- **FileInfo**: Extends FileSystemInfo for file-specific operations, including reading, writing, copying, and moving files.
- **DirectoryInfo**: Extends FileSystemInfo for directory-specific operations, like listing contents, calculating directory size, and recursive deletion.

## Usage

### Working with Files

```
from  YourPackageName.fileinfo  import  FileInfo 

file = FileInfo('/path/to/your/file.txt')
print(file.creation_time) file.copy_to('/path/to/destination/file.txt', overwrite=True)
```

### Working with Directories

```
from  YourPackageName.directoryinfo  import  DirectoryInfo 

directory = DirectoryInfo('/path/to/your/directory')
print(directory.length)  # Total size of files in the directory  for  file_info  in  directory.get_files():
	print(file_info.name)
```

## Contributing

Contributions are welcome! Please feel free to submit a pull request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.