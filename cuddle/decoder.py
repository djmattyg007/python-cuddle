from __future__ import annotations

from functools import partial
from typing import Any, Callable, List, Optional, Sequence

import tatsu.exceptions
from tatsu.ast import AST

from ._escaping import named_escapes
from .exception import KDLDecodeError
from .grammar import KdlParser
from .structure import Document, Node, NodeList


FactoryTypeParam = Optional[str]
IntFactory = Callable[[FactoryTypeParam, str, int], Any]
FloatFactory = Callable[[FactoryTypeParam, str], Any]
StrFactory = Callable[[FactoryTypeParam, str], Any]

ast_parser = KdlParser(whitespace="", parseinfo=False)

exists: Callable[[AST, str], bool] = (
    lambda ast, name: ast is not None and name in ast and ast[name] is not None
)


def _make_decoder(
    _int_factory: IntFactory,
    _float_factory: FloatFactory,
    _str_factory: StrFactory,
    _ignore_unknown_types: bool,
):
    def parse_string(ast: AST, /):
        if not exists(ast, "escstring"):
            return ast["rawstring"]

        val = ""
        for elem in ast["escstring"]:
            if exists(elem, "char"):
                val += elem["char"]
            elif exists(elem, "escape"):
                esc = elem["escape"]
                if exists(esc, "named"):
                    val += named_escapes[esc["named"]]
                else:
                    val += chr(int(esc["unichar"], 16))

        return val

    def parse_identifier(ast: AST, /) -> str:
        if exists(ast, "bare"):
            return "".join(ast["bare"])

        return parse_string(ast["string"])

    def parse_value(ast: AST, /) -> Any:
        val = ast["value"]
        if exists(val, "boolean"):
            return val["boolean"] == "true"
        elif exists(val, "null"):
            return None

        val_type: Optional[str] = None
        if exists(ast, "type"):
            val_type = parse_identifier(ast["type"])

        fallback_factory: Callable[[str], Any]
        if exists(val, "hex"):
            raw_value = val["hex"].replace("_", "")
            sanitised_value = raw_value[0] + raw_value[3:] if raw_value[0] != "0" else raw_value[2:]
            retval = _int_factory(val_type, sanitised_value, 16)
            fallback_factory = partial(int, base=16)
        elif exists(val, "octal"):
            raw_value = val["octal"].replace("_", "")
            sanitised_value = raw_value[0] + raw_value[3:] if raw_value[0] != "0" else raw_value[2:]
            retval = _int_factory(val_type, sanitised_value, 8)
            fallback_factory = partial(int, base=8)
        elif exists(val, "binary"):
            raw_value = val["binary"].replace("_", "")
            sanitised_value = raw_value[0] + raw_value[3:] if raw_value[0] != "0" else raw_value[2:]
            retval = _int_factory(val_type, sanitised_value, 2)
            fallback_factory = partial(int, base=2)
        elif exists(val, "decimal"):
            raw_value = val["decimal"].replace("_", "")
            sanitised_value = raw_value
            if "." in raw_value or "e" in raw_value or "E" in raw_value:
                retval = _float_factory(val_type, sanitised_value)
                fallback_factory = float
            else:
                retval = _int_factory(val_type, sanitised_value, 10)
                fallback_factory = partial(int, base=10)
        elif exists(val, "escstring") or exists(val, "rawstring"):
            raw_value = parse_string(val)
            sanitised_value = raw_value
            retval = _str_factory(val_type, sanitised_value)
            fallback_factory = lambda x: x
        else:
            raise KDLDecodeError(f"Unknown AST node! Internal failure: {val!r}")

        if retval is not None:
            return retval

        if val_type is None or _ignore_unknown_types:
            return fallback_factory(sanitised_value)

        raise KDLDecodeError(f"Failed to decode value '{raw_value}'.")

    def parse_args_and_props(ast: Sequence[AST], /):
        args = []
        props = {}
        for elem in ast:
            if exists(elem, "commented"):
                continue
            if exists(elem, "prop"):
                props[parse_identifier(elem["prop"]["name"])] = parse_value(elem["prop"]["value"])
            else:
                args.append(parse_value(elem["value"]))
        return props, args

    def parse_node(ast: AST, /) -> Optional[Node]:
        if len(ast) == 0 or exists(ast, "commented"):
            return None

        name = parse_identifier(ast["name"])
        args = []
        props = {}
        children = []

        if exists(ast, "args_and_props"):
            props, args = parse_args_and_props(ast["args_and_props"])

        if exists(ast, "children") and not exists(ast["children"], "commented"):
            children = parse_nodes(ast["children"]["children"])

        node_type: Optional[str] = None
        if exists(ast, "type"):
            node_type = parse_identifier(ast["type"])

        return Node(name, node_type, arguments=args, properties=props, children=NodeList(children))

    def parse_nodes(ast: Sequence[AST], /) -> List[Node]:
        if ast[0] == [None] or (
            isinstance(ast[0], list) and len(ast[0]) > 0 and isinstance(ast[0][0], str)
        ):
            # TODO: Figure out why empty documents are so strangely handled
            return []

        nodes = map(parse_node, ast)
        return list(filter(None, nodes))

    return parse_nodes


def extended_str_parser(val_type: Optional[str], val: str) -> Any:
    from base64 import b64decode
    from datetime import date, datetime, time
    from decimal import Decimal
    from ipaddress import IPv4Address, IPv6Address
    from re import compile as re_compile
    from urllib.parse import urlparse
    from uuid import UUID

    if val_type == "base64":
        return b64decode(val, validate=True)
    elif val_type == "date-time" or val_type == "datetime":
        return datetime.fromisoformat(val)
    elif val_type == "date":
        return date.fromisoformat(val)
    elif val_type == "time":
        return time.fromisoformat(val)
    elif val_type == "decimal":
        return Decimal(val)
    elif val_type == "ipv4":
        return IPv4Address(val)
    elif val_type == "ipv6":
        return IPv6Address(val)
    elif val_type == "regex":
        return re_compile(val)
    elif val_type == "url":
        return urlparse(val)
    elif val_type == "uuid":
        return UUID(val)


class KDLDecoder:
    def __init__(
        self,
        *,
        parse_int: Optional[IntFactory] = None,
        parse_float: Optional[FloatFactory] = None,
        parse_str: Optional[StrFactory] = None,
        ignore_unknown_types: bool = False,
    ):
        self.parse_int: IntFactory = parse_int or (lambda _, val, base: int(val, base=base))
        self.parse_float: FloatFactory = parse_float or (lambda _, val: float(val))
        self.parse_str: StrFactory = parse_str or extended_str_parser
        self.ignore_unknown_types = ignore_unknown_types

    def decode(self, s: str, /) -> Document:
        try:
            ast = ast_parser.parse(s)
        except tatsu.exceptions.ParseException as e:
            raise KDLDecodeError("Failed to parse the document.") from e

        decoder = _make_decoder(
            self.parse_int, self.parse_float, self.parse_str, self.ignore_unknown_types
        )

        return Document(NodeList(decoder(ast)))


__all__ = (
    "KDLDecoder",
    "IntFactory",
    "FloatFactory",
    "StrFactory",
    "extended_str_parser",
)
