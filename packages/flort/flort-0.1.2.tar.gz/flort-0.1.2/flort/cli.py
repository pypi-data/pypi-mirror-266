import os
import argparse
from pathlib import Path


def clean_content(file_path):
    """Cleans up the content of a file by removing unnecessary whitespace."""
    with open(file_path, 'r') as file:
        lines = file.readlines()
        cleaned_lines = [line.strip() for line in lines if line.strip()]
        return '\n'.join(cleaned_lines)

def generate_tree(directory):
    """Generates a tree structure of the given directory, ignoring .git folders."""
    tree_structure = ''
    for root, dirs, files in os.walk(directory):
        if '.git' in dirs:
            dirs.remove('.git')  # Ignore .git folder
        level = root.replace(directory, '').count(os.sep)
        indent = '|   ' * level + '|-- '
        tree_structure += f"{indent}{os.path.basename(root)}/\n"
        sub_indent = '|   ' * (level + 1) + '|-- '
        for file in files:
            tree_structure += f"{sub_indent}{file}\n"
    return tree_structure


def list_files(directory, compress=False, extensions=None):
    """Lists files in the given directory with optional compression."""
    directory_path = Path(directory)
    if not directory_path.is_dir():
        print(f"The path {directory} is not a valid directory.")
        return
    
    print(f"Processing directory: {directory_path}")
    
    files_info = ""
    num_files = 0
    for file_path in directory_path.rglob('*'):
        if file_path.is_file() and '.git' not in file_path.parts:
            if extensions is None or file_path.suffix.lower() in extensions:
                num_files += 1
                file_info = f"Path: {file_path}\n"
                file_info += f"File: {file_path.name}\n"
                file_info += "-------\n"

                if compress:
                    compressed_content = clean_content(file_path)
                    file_info += compressed_content
                else:
                    with open(file_path, 'r') as f:
                        file_data = f.read()
                        file_info += file_data
                    
                files_info += file_info
    
    print(f"Number of eligible files processed: {num_files}")
    return files_info

def write_file(file_path,data):
    """Writes data to the specified file."""
    with open(file_path, 'w') as file:
        file.write(data)
    print("Output written to file.")

def main():
    """Main function to parse arguments and execute operations."""
    parser = argparse.ArgumentParser(description="%(prog): List and optionally compress files in a directory.")
    parser.add_argument('--dir', required=True, type=str, help='Directory to list files from.')
    parser.add_argument('--compress', default=False, action='store_true', help='Compress the listed files by removing whitespace.')
    parser.add_argument('--output', type=str, default="stdio", help='Output file path. Defaults to stdout if not specified.')
    parser.add_argument('--php', action='store_true', help='Include PHP files.')
    parser.add_argument('--js', action='store_true', help='Include JavaScript files.')
    parser.add_argument('--py', action='store_true', help='Include Python files.')
    parser.add_argument('--c', action='store_true', help='Include C files.')
    parser.add_argument('--cpp', action='store_true', help='Include C++ files.')    
    parser.add_argument('--no-tree', action='store_true', help='Dont print the tree at the beginning.')    
    args = parser.parse_args()
    
    extensions = []
    output = []
    if args.php:
        extensions.append('.php')
    if args.js:
        extensions.append('.js')
    if args.py:
        extensions.append('.py')
    if args.c:
        extensions.append('.c')
        extensions.append('.h')
    if args.cpp:
        extensions.append('.cpp')
        extensions.append('.h')
    if args.no_tree != True:
        output.append(generate_tree(args.dir))
    
    output.append(list_files(args.dir, compress=args.compress, extensions=extensions))

    if args.output != "stdio":    
        write_file(args.output, "\n".join(output))
    else:
        print("\n".join(output))

if __name__ == "__main__":
    main()
