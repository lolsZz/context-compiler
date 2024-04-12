# Context Compiler

Context Compiler is a tool that generates formatted context from GitHub repositories or local folders. It simplifies the process of extracting and organizing relevant information from code files, making it easier to understand and navigate projects.

## Features

- Generate formatted context from GitHub repositories or local folders
- Customize file inclusion and exclusion options
- Support for various programming languages and file types
- Intuitive command-line interface
- Detailed summary of processed files and output

## Installation

1. Clone the repository:
   ```
   git clone https://github.com/yourusername/context-compiler.git
   ```

2. Navigate to the project directory:
   ```
   cd context-compiler
   ```

3. Install the required dependencies:
   ```
   pip install -r requirements.txt
   ```

## Usage

To generate formatted context from a GitHub repository:
```
python main.py --mode github --url https://github.com/username/repository
```

To generate formatted context from a local folder:
```
python main.py --mode folder --path /path/to/folder
```

For more advanced usage and customization options, refer to the [User Guide](docs/user-guide.md).

## Contributing

Contributions are welcome! If you'd like to contribute to Context Compiler, please follow the guidelines outlined in [CONTRIBUTING.md](CONTRIBUTING.md).

## License

This project is licensed under the [MIT License](LICENSE).
