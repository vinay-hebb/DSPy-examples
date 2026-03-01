"""Utility module for saving DSPy LM responses to files."""

import os
import io
import re
import contextlib

# ANSI color code pattern for stripping when checking for empty lines
ANSI_ESCAPE = re.compile(r'\x1b\[[0-9;]*m')


def save_response(lm, filepath):
    """
    Save the full prompt and response from history to a file using lm.inspect_history().

    Args:
        lm: DSPy language model instance with inspect_history() method
        filepath: Path where the response will be saved
    """
    # Create directory if it doesn't exist
    directory = os.path.dirname(filepath)
    if directory and not os.path.exists(directory):
        os.makedirs(directory)

    # Capture the output of lm.inspect_history(n=1)
    f = io.StringIO()
    with contextlib.redirect_stdout(f):
        lm.inspect_history(n=1)
    history_content = f.getvalue()

    # Strip all empty lines (including whitespace-only lines and lines with only ANSI codes)
    lines = history_content.splitlines(keepends=True)
    history_content = ''.join(
        line for line in lines
        if ANSI_ESCAPE.sub('', line).strip() != ''
    )

    with open(filepath, "w", encoding='utf-8') as f:
        f.write(history_content)
    print(f"Response saved to {filepath}")
