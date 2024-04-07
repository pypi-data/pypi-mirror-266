from __future__ import annotations

import re
import sys

from .flags import COLLAPSE_OUTPUT, COMMAND_FLAG, FLAGS, HIDE, HIDE_INPUT, HIDE_OUTPUT

if sys.version_info.minor < 9:  # pragma: no cover
    from typing import Pattern

    rePattern = Pattern[str]
else:
    rePattern = re.Pattern[str]


def generate_flags_string(flags: list[str]) -> str:
    """Generate re pattern from list of flags, add flags with '-' instead of '_'.

    Args:
        flags (List[str]): List of flags.

    Returns:
        str: flags, separated by '|'
    """
    result_flags = flags.copy()
    for item in flags:
        if "_" in item:
            result_flags.append(item.replace("_", "-"))
    return "|".join(result_flags)


def get_flags_re(flags: list[str]) -> rePattern:
    """Create Regex pattern from list of flags.

    Args:
        flags (List[str]): List of flags.

    Returns:
        re.Pattern: Regex pattern.
    """
    flag_string = generate_flags_string(flags)
    pattern = rf"^\s*{COMMAND_FLAG}\s*({flag_string})\s*\n*$"
    return re.compile(pattern, re.M)


re_flags = get_flags_re(FLAGS)
re_hide = get_flags_re(HIDE)
re_hide_input = get_flags_re(HIDE_INPUT)
re_hide_output = get_flags_re(HIDE_OUTPUT)
# re_collapse = get_flags_re([COLLAPSE_OUTPUT])
re_collapse = re.compile(
    rf"^\s*\#\s*({generate_flags_string([COLLAPSE_OUTPUT])})\s*\n*",
    re.M,
)
re_output_code = get_flags_re(["output_code"])
re_code_cell_marker = re.compile(r"```\w*\s*\n")
re_cell = re.compile(
    r"^(<!--\scell\s*#(?:\d+)\s*(markdown|code|raw)\s*-->)\n\n",
    flags=re.M,
)
