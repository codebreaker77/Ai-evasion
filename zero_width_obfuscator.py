"""Zero-Width Space Text Obfuscator.

Inserts invisible zero-width Unicode characters into text to alter
tokenization and character sequences without affecting visual readability.
"""

from __future__ import annotations

import argparse
import random
import sys

# Ensure UTF-8 output encoding on Windows consoles
if hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
        sys.stdin.reconfigure(encoding="utf-8")
    except Exception:
        pass

# Common zero-width Unicode characters
ZERO_WIDTH_CHARS = [
    "\u200B",  # Zero-Width Space (ZWSP)
    "\u200C",  # Zero-Width Non-Joiner (ZWNJ)
    "\u200D",  # Zero-Width Joiner (ZWJ)
    "\uFEFF",  # Zero-Width No-Break Space (BOM)
]


def copy_to_clipboard(text: str) -> bool:
    """Copies text to the system clipboard using standard library tkinter."""
    try:
        import tkinter
        root = tkinter.Tk()
        root.withdraw()
        root.clipboard_clear()
        root.clipboard_append(text)
        root.update()
        root.destroy()
        return True
    except Exception:
        return False


def insert_zero_width_spaces(
    text: str,
    probability: float = 0.25,
    chars: list[str] | None = None,
    inside_words_only: bool = True,
) -> str:
    """Inserts zero-width characters randomly into the provided text.

    Args:
        text: Input string.
        probability: Probability (0.0 to 1.0) of inserting a character at each valid position.
        chars: List of zero-width characters to sample from. Defaults to ZERO_WIDTH_CHARS.
        inside_words_only: If True, only injects between alphanumeric characters to preserve
                           spaces and punctuation integrity.

    Returns:
        The obfuscated text containing invisible zero-width characters.
    """
    if not text:
        return text

    if chars is None:
        chars = ZERO_WIDTH_CHARS

    result: list[str] = []
    text_len = len(text)

    for i, char in enumerate(text):
        result.append(char)

        # Do not insert after the last character
        if i >= text_len - 1:
            continue

        next_char = text[i + 1]

        # Determine if this position is eligible
        if inside_words_only:
            eligible = char.isalnum() and next_char.isalnum()
        else:
            eligible = not char.isspace() and not next_char.isspace()

        if eligible and random.random() < probability:
            result.append(random.choice(chars))

    return "".join(result)


def strip_zero_width_spaces(text: str, chars: list[str] | None = None) -> str:
    """Removes all zero-width characters from the text.

    Args:
        text: Input string containing zero-width characters.
        chars: List of characters to strip. Defaults to ZERO_WIDTH_CHARS.

    Returns:
        Cleaned text.
    """
    if chars is None:
        chars = ZERO_WIDTH_CHARS

    for c in chars:
        text = text.replace(c, "")
    return text


def count_zero_width_spaces(text: str, chars: list[str] | None = None) -> int:
    """Counts how many zero-width characters exist in the given text."""
    if chars is None:
        chars = ZERO_WIDTH_CHARS
    return sum(text.count(c) for c in chars)


def main():
    parser = argparse.ArgumentParser(
        description="Insert invisible zero-width spaces into text to disrupt AI detectors."
    )
    parser.add_argument(
        "-t", "--text", type=str, help="Text to process directly via command-line argument."
    )
    parser.add_argument(
        "-i", "--input", type=str, help="Path to input text file."
    )
    parser.add_argument(
        "-o", "--output", type=str, help="Path to output text file."
    )
    parser.add_argument(
        "-r",
        "--rate",
        type=float,
        default=0.25,
        help="Probability of injecting a zero-width space between letters (default: 0.25).",
    )
    parser.add_argument(
        "-c",
        "--clipboard",
        action="store_true",
        help="Automatically copy the resulting text to your clipboard.",
    )
    parser.add_argument(
        "--clean",
        action="store_true",
        help="Clean/strip existing zero-width spaces from the text.",
    )
    parser.add_argument(
        "--all-positions",
        action="store_true",
        help="Inject between any non-space characters, not just inside words.",
    )

    args = parser.parse_args()

    # Determine input text
    if args.text:
        source_text = args.text
    elif args.input:
        with open(args.input, "r", encoding="utf-8") as f:
            source_text = f.read()
    else:
        print("Enter or paste your text below (press Ctrl+Z and then Enter on Windows to finish):")
        source_text = sys.stdin.read()

    if not source_text.strip():
        print("Error: No text provided.", file=sys.stderr)
        sys.exit(1)

    if args.clean:
        output_text = strip_zero_width_spaces(source_text)
        removed_count = len(source_text) - len(output_text)
        print(f"[Info] Removed {removed_count} invisible characters.", file=sys.stderr)
    else:
        output_text = insert_zero_width_spaces(
            source_text,
            probability=args.rate,
            inside_words_only=not args.all_positions,
        )
        injected_count = count_zero_width_spaces(output_text)
        print(f"[Info] Injected {injected_count} invisible zero-width characters.", file=sys.stderr)

    # Handle output file
    if args.output:
        with open(args.output, "w", encoding="utf-8") as f:
            f.write(output_text)
        print(f"[Success] Output written to {args.output}", file=sys.stderr)

    # Handle clipboard
    if args.clipboard:
        if copy_to_clipboard(output_text):
            print("[Success] Result copied to clipboard!", file=sys.stderr)
        else:
            print("[Warning] Could not access clipboard.", file=sys.stderr)

    # Print to console if not saving solely to a file, or if explicit
    if not args.output or not args.clipboard:
        print("\n--- Processed Text (looks normal visually) ---")
        try:
            print(output_text)
        except UnicodeEncodeError:
            # Fallback if console still cannot display
            print(output_text.encode("utf-8", errors="replace").decode("utf-8"))


if __name__ == "__main__":
    main()
