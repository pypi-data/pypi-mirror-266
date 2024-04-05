Here's a README for your project:

---

# Pancake

Pancake is a command-line tool for listing and optionally cleaning up files in a directory.

## Installation

You can install Pancake via pip:

```
pip install pancake
```

## Usage

Pancake provides various options for listing and cleaning up files in a directory.

```
pancake --dir <directory_path> [--compress] [--output <output_file>] [--php] [--js] [--py] [--c] [--cpp] [--tree]
```

### Options

- `--dir`: Specify the directory to list files from (required).
- `--compress`: Clean up files by removing unnecessary whitespace (optional).
- `--output`: Specify the output file path (default: stdout).
- `--php`, `--js`, `--py`, `--c`, `--cpp`: Include specific file types in the listing (optional).
- `--tree`: Print the directory tree at the beginning of the output (optional).

## Examples

List files in a directory and include PHP files:

```
pancake --dir /path/to/directory --php
```

Clean up files in a directory and save the output to a file:

```
pancake --dir /path/to/directory --compress --output output.txt
```

List files in a directory, include JavaScript and Python files, and print the directory tree:

```
pancake --dir /path/to/directory --js --py --tree
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

--- 

You might need to provide additional information about the project's dependencies, how to contribute, or any other relevant details depending on your specific project requirements.