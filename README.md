# AI Evasion

A utility and local web interface that inserts non-printing zero-width Unicode characters into text to disrupt tokenization in automated classifiers while preserving visual readability.

## Overview

Natural language processing pipelines and automated text classifiers rely on subword tokenizers (such as Byte-Pair Encoding and WordPiece) to convert text into token IDs. Inserting zero-width characters breaks expected character sequences inside words, altering the resulting token streams, perplexity metrics, and burstiness statistics without changing how the text appears to a human reader.

Supported zero-width characters:
- U+200B: Zero-Width Space (ZWSP)
- U+200C: Zero-Width Non-Joiner (ZWNJ)
- U+200D: Zero-Width Joiner (ZWJ)
- U+FEFF: Zero-Width No-Break Space (BOM)

## Features

- Local web interface with real-time text processing
- Light mode (solid white) and dark mode
- Inspector view showing exact locations of inserted characters
- Command-line interface with file and clipboard support
- Function to strip zero-width characters and restore raw text
- Zero external dependencies (uses standard library Python)

## Installation

Clone the repository:

```bash
git clone https://github.com/codebreaker77/Ai-evasion.git
cd Ai-evasion
```

Python 3.7 or newer is required. No external packages are needed.

## Web Interface

Start the local server:

```bash
python app.py
```

The application will start on `http://localhost:5000` and automatically open in your default browser.

Alternatively, `index.html` can be opened directly in any web browser without running a server.

## Command-Line Usage

### Process text directly
```bash
python zero_width_obfuscator.py --text "Input text here"
```

### Copy result directly to clipboard
```bash
python zero_width_obfuscator.py --text "Input text here" -c
```

### Process an input file and write to an output file
```bash
python zero_width_obfuscator.py -i input.txt -o output.txt -r 0.25
```

### Strip existing zero-width characters
```bash
python zero_width_obfuscator.py -i obfuscated.txt --clean -o cleaned.txt
```

### Command-line options

- `-t`, `--text`: Input text string.
- `-i`, `--input`: Path to input file.
- `-o`, `--output`: Path to output file.
- `-r`, `--rate`: Insertion frequency between 0.0 and 1.0 (default: 0.25).
- `-c`, `--clipboard`: Copy output directly to system clipboard.
- `--clean`: Remove all zero-width characters from the text.
- `--all-positions`: Insert between any non-space characters instead of inside alphanumeric words only.

## Python Library Usage

```python
from zero_width_obfuscator import insert_zero_width_spaces, strip_zero_width_spaces

# Insert zero-width spaces
text = "Sample sentence."
obfuscated = insert_zero_width_spaces(text, probability=0.3)

# Remove zero-width spaces
cleaned = strip_zero_width_spaces(obfuscated)
```

## License

MIT
