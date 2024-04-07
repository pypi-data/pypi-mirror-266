"""Helpers for lib."""

from typing import Union


StrListStr = Union[str, list[str], None]


def get_code(filename: str, lang: str = "python") -> str:
    """get code from file"""
    with open(filename, "r", encoding="utf-8") as f:
        return f"```{lang}\n{f.read()}\n```"


def validate_args(args: StrListStr) -> list[str]:
    if isinstance(args, str):
        args = [args]
    elif args is None:
        args = []
    return args


# termynal output.
# termynal - animated terminal window. https://github.com/daxartio/termynal
# based on https://github.com/ines/termynal - termynal.js
def termynal_output(
    starter: str = "python",
    prog: str = "my_app.py",
    args: StrListStr = None,
    out_text: str = "",
) -> str:
    """print termynal output"""
    args_str = " ".join(validate_args(args))
    lines = [
        "<!-- termynal -->",
        "```",
        f"$ {starter} {prog} {args_str}",
        out_text,
        "\n```",
    ]
    return "\n".join(lines)
