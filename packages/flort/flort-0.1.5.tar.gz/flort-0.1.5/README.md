# flort

flort is a command-line tool for generating a single file with the contents of your code directories.. for use in LLMs.

## Installation

You can install flort via pip:

```
pip install flort
```

## Usage

flort provides various options for listing and cleaning up files in a directory.

```bash
flort <directory_path> [--compress] [--output <output_file>] [--php] [--js] [--py] [--c] [--cpp] [--no-tree]
```

### Options

- `--compress`: Clean up files by removing unnecessary whitespace (optional).
- `--output`: Specify the output file path (default: stdout).
- `--php`, `--js`, `--py`, `--c`, `--cpp`: Include specific file types in the listing (optional).
- `--no-tree`: Do not print the directory tree at the beginning of the output (optional).

## Examples

List files in a directory and include PHP files:

```
flort /path/to/directory --php
```

Clean up files in a directory and save the output to a file:

```
flort /path/to/directory --compress --output output.txt
```

List files in a directory, include JavaScript and Python files, and do not print the directory tree:

```
flort /path/to/directory --js --py --no-tree
```

## License

This project is licensed under the BSD 3-Clause License - see the [LICENSE](LICENSE) file for details.

