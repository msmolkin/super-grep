# Super Grep

[![GitHub stars](https://img.shields.io/github/stars/msmolkin/super-grep.svg)](https://github.com/msmolkin/super-grep/stargazers)
[![GitHub license](https://img.shields.io/github/license/msmolkin/super-grep.svg)](https://github.com/msmolkin/super-grep/blob/master/LICENSE)
[![PyPI version](https://badge.fury.io/py/super-grep.svg)](https://badge.fury.io/py/super-grep)
[![Donate](https://img.shields.io/badge/Donate-PayPal-green.svg)](https://www.paypal.com/cgi-bin/webscr?cmd=_s-xclick&hosted_button_id=YOUR_PAYPAL_BUTTON_ID)

Super Grep is a powerful, format-agnostic search tool that allows you to search for patterns in files and directories with ease. It supports various naming conventions and provides options for controlling search depth, file content searching, and output colorization.

## Features

- Format-agnostic pattern matching (supports camelCase, snake_case, PascalCase, kebab-case, Title Case, Capitalized With Spaces, etc.)
- Configurable search depth
- File content searching
- Colorized output
- Multi-processing for improved performance

## Installation

You can install Super Grep using pip:

```
pip install super-grep
```

## Usage

After installation, you can use the `super-grep` command directly from your terminal:

```
super-grep [OPTIONS] DIRECTORY PATTERN
```

### Options

- `--workers NUMBER`: Number of worker processes (default: CPU count)
- `--contents`: Search within file contents (default: search filenames only)
- `--color`: Colorize the output
- `--depth NUMBER`: Depth of directory search (default: 0, search only in given directory; use -1 for unlimited depth)

### Examples

1. Search only in the given directory:
   ```
   super-grep /path/to/search "FooBar|first_name"
   ```

2. Search up to 2 levels deep:
   ```
   super-grep /path/to/search "FooBar|first_name" --depth 2
   ```

3. Search all subdirectories:
   ```
   super-grep /path/to/search "FooBar|first_name" --depth -1
   ```

4. Search file contents up to 3 levels deep with colored output:
   ```
   super-grep /path/to/search "FooBar|first_name" --depth 3 --contents --color
   ```

5. Use 8 worker processes:
   ```
   super-grep /path/to/search "FooBar|first_name" --workers 8
   ```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.