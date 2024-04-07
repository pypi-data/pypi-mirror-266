from __future__ import annotations

import re
import sys


if sys.version_info.minor < 9:  # pragma: no cover
    from typing import Pattern

    rePattern = Pattern[str]
else:
    rePattern = re.Pattern[str]

# Flags
# Flag is starts with #!, at start of the line, no more symbols at this line except whitespaces.
# future request - command_flag wil be at cfg
COMMAND_FLAG = "#!"
HIDE = ["hide"]  # hide cell
HIDE_INPUT = ["hide_input"]  # hide code from this cell
HIDE_OUTPUT = ["hide_output"]  # hide output from this cell

HIDE_FLAGS = HIDE + HIDE_INPUT + HIDE_OUTPUT

FLAGS: list[str] = [] + HIDE_FLAGS  # here will be more flags.

COLLAPSE_OUTPUT = "collapse_output"

CELL_FLAG = "###cell\n"
