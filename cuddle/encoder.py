from __future__ import annotations

from typing import Any, Callable, Iterable, Optional, Tuple, Union

import regex

from ._escaping import named_escape_inverse
from .exception import KDLEncodeTypeError
from .structure import Document, Node


IdentifierFormatter = Callable[[str], str]
ValueEncoderResult = Union[None, str, Tuple[Optional[str], str]]
ValueEncoder = Callable[[Any, IdentifierFormatter], ValueEncoderResult]


ident_re = regex.compile(
    r'^[^/\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^/\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$'
)

_intstr = int.__repr__
_floatstr = float.__repr__


def _make_encoder(
    _indent: str, _value_encoder: ValueEncoder
) -> Callable[[Document], Iterable[str]]:
    def format_string(val: str, /) -> str:
        if "\\" in val and '"' not in val:
            return 'r#"%s"#' % val

        inner = "".join(
            "\\" + named_escape_inverse[c] if c in named_escape_inverse else c for c in val
        )
        return f'"{inner}"'

    def format_identifier(ident: str, /) -> str:
        if ident_re.match(ident) and ident not in ("true", "false", "null"):
            return ident
        else:
            return format_string(ident)

    def format_value(val: Any, /) -> str:
        result = _value_encoder(val, format_identifier)
        if result is None:
            raise KDLEncodeTypeError(
                f"Object of type {val.__class__.__name__} is not KDL serializable"
            )

        if isinstance(result, str):
            return result

        value_type, value_string = result
        if value_type is not None:
            return f"({format_identifier(value_type)}){format_string(value_string)}"
        else:
            return format_string(value_string)

    def format_node(node: Node, /, *, top_level: bool = False) -> Iterable[str]:
        if top_level:
            indent = ""
        else:
            indent = _indent
            yield indent

        if node.node_type is not None:
            yield f"({format_identifier(node.node_type)})"
        yield format_identifier(node.name)

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


def default_value_encoder(val: Any, _ident_fmt: IdentifierFormatter, /) -> ValueEncoderResult:
    if val is None:
        return "null"
    elif isinstance(val, bool):
        return "true" if val else "false"
    elif isinstance(val, int):
        return _intstr(val)
    elif isinstance(val, float):
        return _floatstr(val)

    if isinstance(val, str):
        return None, val

    from decimal import Decimal

    if isinstance(val, Decimal):
        return "decimal", str(val)


def extended_value_encoder(val: Any, ident_fmt: IdentifierFormatter, /) -> ValueEncoderResult:
    default_result = default_value_encoder(val, ident_fmt)
    if default_result is not None:
        return default_result

    from base64 import b64encode
    from datetime import date, datetime, time
    from ipaddress import IPv4Address, IPv6Address
    from re import Pattern as RePattern
    from urllib.parse import DefragResult as UrlDefragResult
    from urllib.parse import ParseResult as UrlParseResult
    from urllib.parse import SplitResult as UrlSplitResult
    from uuid import UUID

    if isinstance(val, bytes):
        return "base64", b64encode(val).decode("utf-8")
    elif isinstance(val, datetime):
        return "date-time", val.isoformat()
    elif isinstance(val, date):
        return "date", val.isoformat()
    elif isinstance(val, time):
        return "time", val.isoformat()
    elif isinstance(val, IPv4Address):
        return "ipv4", str(val)
    elif isinstance(val, IPv6Address):
        return "ipv6", str(val)
    elif isinstance(val, (RePattern, regex.Pattern)):
        return "regex", val.pattern
    elif isinstance(val, (UrlDefragResult, UrlParseResult, UrlSplitResult)):
        return "url", val.geturl()
    elif isinstance(val, UUID):
        return "uuid", str(val)


class KDLEncoder:
    def __init__(
        self,
        *,
        indent: Union[str, int, None] = None,
        value_encoder: Optional[ValueEncoder] = None,
    ):
        self.indent: str
        if isinstance(indent, str):
            self.indent = indent
        elif isinstance(indent, int):
            self.indent = " " * indent
        else:
            self.indent = "  "

        self.value_encoder: ValueEncoder
        if value_encoder is not None:
            self.value_encoder = value_encoder
        else:
            self.value_encoder = extended_value_encoder

    def encode(self, doc: Document) -> str:
        chunks = self.iterencode(doc)
        if not isinstance(chunks, (list, tuple)):
            chunks = list(chunks)
        return "".join(chunks)

    def iterencode(self, doc: Document) -> Iterable[str]:
        encoder = _make_encoder(self.indent, self.value_encoder)
        return encoder(doc)


__all__ = (
    "KDLEncoder",
    "IdentifierFormatter",
    "ValueEncoder",
    "ValueEncoderResult",
    "default_value_encoder",
    "extended_value_encoder",
)
