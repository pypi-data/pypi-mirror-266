from typing import Any, BinaryIO

from lark import Discard, Lark, Transformer

_opt_parser = Lark(
    r"""
    ?pairvalueopts: SIGNED_NUMBER | QUOTEDSTRING | SIMPLESTRING

    pairvalue: pairvalueopts (" " pairvalueopts)*

    dictt: TAB* "{" IDENTIFIER NEWLINE core+ TAB* "}" NEWLINE

    pair: TAB* IDENTIFIER " " pairvalue NEWLINE

    core: (pair | dictt)*

    TAB: "\t" | "    "
    IDENTIFIER: SIMPLESTRING
    QUOTEDSTRING: ESCAPED_STRING
    SIMPLESTRING: (LETTER | DIGIT | ".")+

    %import common.ESCAPED_STRING
    %import common.SIGNED_NUMBER
    %import common.DIGIT
    %import common.LETTER
    %import common.WS
    %import common.NEWLINE
    """,
    start="core",
)
# ^ magic


class _OptTransformer(Transformer):
    def NEWLINE(self, tok: str):
        # ditch whitespace
        return Discard

    def TAB(self, tok: str):
        # ditch whitespace
        return Discard

    def SIGNED_NUMBER(self, tok: str) -> int | float:
        if "." in tok:
            return float(tok)

        return int(tok)

    def QUOTEDSTRING(self, tok: str) -> str:
        # remove surrounding quotes
        return tok[1:-1]

    def pairvalue(self, tok: list[str | float | int]):
        # return single value
        if len(tok) == 1:
            return tok[0]

        # keep list as lists
        return tok

    def pair(self, tok: tuple[str, Any]) -> dict[str, Any]:
        # key, value
        return {tok[0]: tok[1]}

    def dictt(self, tok: tuple[str, Any]) -> dict[str, Any]:
        # key, value, identifier is already recorded
        return {tok[0]: tok[1]}

    def core(self, tok: list | dict) -> Any:
        if len(tok) == 1:
            return tok[0]

        # combine dicts
        return {k: v for d in tok for k, v in d.items()}

    IDENTIFIER = str
    SIMPLESTRING = str


def _write_value(value: Any) -> str:
    if isinstance(value, str):
        if '"' in value:
            # i am afraid of undefined behavior
            raise ValueError("Cannot have quotes in string")

        if " " in value:
            return f'"{value}"'

        return value

    if isinstance(value, list):
        return " ".join(_write_value(i) for i in value)

    if isinstance(value, float):
        # the file format seems to always have 6 trailing zeros for floats
        return f"{value:.6f}"

    # this needs to come first, as a bool is technically an int
    if isinstance(value, bool):
        raise ValueError("Unsupported type: bool")

    if isinstance(value, int):
        return str(value)

    raise ValueError(f"Unsupported type: {type(value)}")


def _write_dict(data: dict, level: int = 0) -> str:
    out = ""
    NEWLINE = "\r\n"
    TAB = "\t"

    for k, v in data.items():
        if isinstance(v, dict):
            # write opening brace, key, newline, recursive values, then closing brace
            # and newline
            out += f"{TAB * level}{{{k}\n{_write_dict(v, level + 1)}{TAB * level}}}{NEWLINE}"
        else:
            # write out a key value pair
            out += f"{TAB * level}{k} {_write_value(v)}{NEWLINE}"

    return out


def loads(data: str) -> dict:
    """
    Load UserCfg.opt data from a string.
    """
    tree = _opt_parser.parse(data)
    return _OptTransformer().transform(tree)


def load(fp: BinaryIO) -> dict:
    """
    Load UserCfg.opt data from a file-like object.
    """
    return loads(fp.read().decode())


def dumps(data: dict) -> str:
    """
    Dump data in a UserCfg.opt format to a string.
    """
    return _write_dict(data)


def dump(data: dict, fp: BinaryIO) -> None:
    """
    Dump data in a UserCfg.opt format to a file-like object.
    """
    fp.write(dumps(data).encode())
