from typing import Any, Callable, Iterable, Optional, Union

import regex

from ._escaping import named_escape_inverse
from .structure import Document, Node, Symbol


DefaultHandler = Callable[[Any], str]

ident_re = regex.compile(
    r'^[^\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$'
)


def _make_encoder(_indent: str, _default: DefaultHandler) -> Callable[[Document], Iterable[str]]:
    _intstr = int.__repr__
    _floatstr = float.__repr__

    def format_string(val: str) -> str:
        if "\\" in val and '"' not in val:
            return 'r#"%s"#' % val

        inner = "".join("\\" + named_escape_inverse[c] if c in named_escape_inverse else c for c in val)
        return f'"{inner}"'

    def format_identifier(ident: str) -> str:
        if ident_re.match(ident):
            return ident
        else:
            return format_string(ident)

    def format_value(val: Any) -> str:
        if isinstance(val, Symbol):
            return ":" + format_identifier(val.value)
        elif isinstance(val, str):
            return format_string(val)
        elif val is None:
            return "null"
        elif isinstance(val, bool):
            return "true" if val else "false"
        elif isinstance(val, int):
            return _intstr(val)
        elif isinstance(val, float):
            return _floatstr(val)
        else:
            return _default(val)

    def format_node(node: Node, /, *, top_level: bool = False) -> Iterable[str]:
        if top_level:
            indent = ""
        else:
            indent = _indent

        yield indent + format_identifier(node.name)

        for k, v in node.properties.items():
            yield " {0}={1}".format(format_identifier(k), format_value(v))

        for v in node.arguments:
            yield " " + format_value(v)

        if node.children:
            yield " {\n"
            for child in node.children:
                yield indent
                yield from format_node(child)
                yield "\n"
            yield indent + "}"

    def format_document(document: Document) -> Iterable[str]:
        for node in document.nodes:
            yield from format_node(node, top_level=True)
            yield "\n"

    return format_document


def extended_default(o: Any) -> str:
    from base64 import b64encode
    from datetime import datetime, date, time
    from decimal import Decimal
    from ipaddress import IPv4Address, IPv6Address
    from re import Pattern as RePattern
    from uuid import UUID

    if isinstance(o, bytes):
        return b64encode(o).decode("utf-8")
    elif isinstance(o, datetime):
        return o.isoformat()
    elif isinstance(o, date):
        return o.isoformat()
    elif isinstance(o, time):
        return o.isoformat()
    elif isinstance(o, Decimal):
        return str(o)
    elif isinstance(o, (IPv4Address, IPv6Address)):
        return str(o)
    elif isinstance(o, RePattern):
        return o.pattern
    elif isinstance(o, regex.Pattern):
        return o.pattern
    elif isinstance(o, UUID):
        return str(o)

    raise TypeError(f"Object of type {o.__class__.__name__} is not KDL serializable")


class KDLEncoder:
    def __init__(self, *, indent: Union[str, int, None] = None, default: Optional[DefaultHandler] = None):
        self.indent: str
        if isinstance(indent, str):
            self.indent = indent
        elif isinstance(indent, int):
            self.indent = " " * indent
        else:
            self.indent = "  "

        if default is not None:
            self.default = default

    def default(self, o: Any) -> str:
        raise TypeError(f"Object of type {o.__class__.__name__} is not KDL serializable")

    def encode(self, doc: Document) -> str:
        chunks = self.iterencode(doc)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return "".join(chunks)

    def iterencode(self, doc: Document) -> Iterable[str]:
        encoder = _make_encoder(self.indent, self.default)
        return encoder(doc)


__all__ = (
    "KDLEncoder",
    "DefaultHandler",
    "extended_default",
)
