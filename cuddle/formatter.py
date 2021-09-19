from __future__ import annotations

from typing import Iterable

import regex

from ._escaping import named_escape_inverse
from .structure import Document, Node, Symbol


ident_re = regex.compile(
    r'^[^\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$'
)


def format_string(val: str) -> str:
    if "\\" in val and '"' not in val:
        return 'r#"%s"#' % val

    inner = "".join("\\" + named_escape_inverse[c] if c in named_escape_inverse else c for c in val)
    return f'"{inner}"'


def format_identifier(ident):
    if ident_re.match(ident):
        return ident
    else:
        return format_string(ident)


def format_value(val) -> str:
    if isinstance(val, Symbol):
        return ":" + format_identifier(val.value)
    elif isinstance(val, str):
        return format_string(val)
    elif isinstance(val, bool):
        return "true" if val else "false"
    elif val is None:
        return "null"
    else:
        return str(val)


def format_node(node: Node, /, *, _indent: bool = False) -> str:
    fmt = format_identifier(node.name)

    for k, v in node.properties.items():
        fmt += " {0}={1}".format(format_identifier(k), format_value(v))

    for v in node.arguments:
        fmt += " " + format_value(v)

    if node.children:
        fmt += " {\n"
        for child in node.children:
            fmt += format_node(child, _indent=True) + "\n"
        fmt += "}"

    if not _indent:
        return fmt

    return "\n".join("  " + line for line in fmt.split("\n"))


def format_document(document: Document) -> Iterable[str]:
    for node in document.nodes:
        yield format_node(node) + "\n"


__all__ = (
    "format_node",
    "format_document",
)
