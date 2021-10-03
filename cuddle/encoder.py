from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, Tuple, Union

import regex

from ._escaping import named_escape_inverse
from .structure import Document, Node


DefaultHandlerResult = Tuple[Optional[str], str]
DefaultHandler = Callable[[Any], Optional[DefaultHandlerResult]]

ident_re = regex.compile(
    r'^[^\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$'
)


def _make_encoder(
    _indent: str, _default: Callable[[Any], DefaultHandlerResult]
) -> Callable[[Document], Iterable[str]]:
    _intstr = int.__repr__
    _floatstr = float.__repr__

    def format_string(val: str, /) -> str:
        if "\\" in val and '"' not in val:
            return 'r#"%s"#' % val

        inner = "".join(
            "\\" + named_escape_inverse[c] if c in named_escape_inverse else c for c in val
        )
        return f'"{inner}"'

    def format_identifier(ident: str, /) -> str:
        if ident_re.match(ident):
            return ident
        else:
            return format_string(ident)

    def format_value(val: Any, /) -> str:
        if val is None:
            return "null"
        elif isinstance(val, bool):
            return "true" if val else "false"

        if isinstance(val, str):
            return format_string(val)
        elif isinstance(val, int):
            return _intstr(val)
        elif isinstance(val, float):
            return _floatstr(val)

        value_type, value_string = _default(val)
        if value_type:
            return f"({value_type}){format_string(value_string)}"
        else:
            return format_string(value_string)

    def format_node(node: Node, /, *, top_level: bool = False) -> Iterable[str]:
        if top_level:
            indent = ""
        else:
            indent = _indent

        yield indent + format_identifier(node.name)

        for val in node.arguments:
            yield " " + format_value(val)

        for key, val in node.properties.items():
            yield " {0}={1}".format(format_identifier(key), format_value(val))

        if node.children:
            yield " {\n"
            for child in node.children:
                yield indent
                yield from format_node(child)
                yield "\n"
            yield indent + "}"

    def format_document(document: Document, /) -> Iterable[str]:
        for node in document:
            yield from format_node(node, top_level=True)
            yield "\n"

    return format_document


def extended_default(o: Any) -> Optional[DefaultHandlerResult]:
    from base64 import b64encode
    from datetime import date, datetime, time
    from decimal import Decimal
    from ipaddress import IPv4Address, IPv6Address
    from re import Pattern as RePattern
    from urllib.parse import DefragResult as UrlDefragResult
    from urllib.parse import ParseResult as UrlParseResult
    from urllib.parse import SplitResult as UrlSplitResult
    from uuid import UUID

    if isinstance(o, bytes):
        return "base64", b64encode(o).decode("utf-8")
    elif isinstance(o, datetime):
        return "date-time", o.isoformat()
    elif isinstance(o, date):
        return "date", o.isoformat()
    elif isinstance(o, time):
        return "time", o.isoformat()
    elif isinstance(o, Decimal):
        return "decimal", str(o)
    elif isinstance(o, IPv4Address):
        return "ipv4", str(o)
    elif isinstance(o, IPv6Address):
        return "ipv6", str(o)
    elif isinstance(o, (RePattern, regex.Pattern)):
        return "regex", o.pattern
    elif isinstance(o, (UrlDefragResult, UrlParseResult, UrlSplitResult)):
        return "url", o.geturl()
    elif isinstance(o, UUID):
        return "uuid", str(o)


class KDLEncoder:
    def __init__(
        self,
        *,
        indent: Union[str, int, None] = None,
        default: Optional[DefaultHandler] = None,
        use_extended_default: bool = True,
    ):
        self.indent: str
        if isinstance(indent, str):
            self.indent = indent
        elif isinstance(indent, int):
            self.indent = " " * indent
        else:
            self.indent = "  "

        self.default_handler: Optional[DefaultHandler]
        if default is not None:
            self.default_handler = default
        elif use_extended_default:
            self.default_handler = extended_default
        else:
            self.default_handler = None

    def default(self, o: Any) -> DefaultHandlerResult:
        if self.default_handler:
            result = self.default_handler(o)
            if result is not None:
                return result

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
