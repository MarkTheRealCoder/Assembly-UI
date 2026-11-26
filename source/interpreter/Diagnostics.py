import re
from typing import NamedTuple, Optional


class Diagnostic(NamedTuple):
    """ A problem reported by the interpreter: line from 1, column from 0 (-1 marks the whole line). """
    line: int
    column: int
    token: Optional[str]
    message: str
    severity: str  # "error" or "warning"


_POSITIONED = re.compile(
    r"^(?P<kind>Syntax|Semantic) (?P<level>error|warning) at line (?P<line>\d+):(?P<column>\d+) - (?P<text>.*)$"
)
_NEAR_TOKEN = re.compile(r"\s*\(near token '(?P<token>.*)'\)$")
_RUNTIME = re.compile(r"^Runtime error at line (?P<line>\d+)")
_ESCAPES = {"\\n": "\n", "\\r": "\r", "\\t": "\t"}


def _unescape(token: str) -> str:
    for escaped, char in _ESCAPES.items():
        token = token.replace(escaped, char)
    return token


def parseDiagnostics(text: Optional[str]) -> list[Diagnostic]:
    """
    Extract the positioned errors and warnings from the messages of the interpreter, one per line, such as
    "Syntax error at line 4:9 - no viable alternative at input 'AX,\\n' (near token '\\n')".
    Messages without a position are ignored.
    """
    diagnostics = []
    if not text:
        return diagnostics
    for raw in text.splitlines():
        raw = raw.strip()
        if match := _POSITIONED.match(raw):
            body = match.group("text")
            token = None
            if near := _NEAR_TOKEN.search(body):
                token = near.group("token")
                token = None if token == "<unknown>" else _unescape(token)
            diagnostics.append(Diagnostic(
                int(match.group("line")), int(match.group("column")), token, raw, match.group("level")
            ))
        elif match := _RUNTIME.match(raw):
            diagnostics.append(Diagnostic(int(match.group("line")), -1, None, raw, "error"))
    return diagnostics
