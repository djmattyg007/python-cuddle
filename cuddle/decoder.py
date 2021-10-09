from __future__ import annotations

from functools import partial
from typing import Any, Callable, List, Optional, Sequence

import tatsu.exceptions
from tatsu.ast import AST
from tatsu.contexts import tatsumasu

from ._escaping import named_escapes
from .exception import KDLDecodeError
from .grammar import KdlParser as BaseKdlParser, KdlSemantics as BaseKdlSemantics
from .structure import Document, Node, NodeList


FactoryTypeParam = Optional[str]
NullFactory = Callable[[FactoryTypeParam, str], Any]
BoolFactory = Callable[[FactoryTypeParam, str], Any]
IntFactory = Callable[[FactoryTypeParam, str, int], Any]
FloatFactory = Callable[[FactoryTypeParam, str], Any]
StrFactory = Callable[[FactoryTypeParam, str], Any]


def _strflatten(iterable) -> str:
    result = ""
    for item in iterable:
        if isinstance(item, str):
            result += item
        else:
            result += _strflatten(item)
    return result


def _clean_nondecimal_number(raw_value: str) -> str:
    cleaned_value = raw_value.replace("_", "")
    if cleaned_value[0] == "0":
        sanitised_value = cleaned_value[2:]
    else:
        sanitised_value = cleaned_value[0] + cleaned_value[3:]

    return sanitised_value


class KDLParser(BaseKdlParser):
    @tatsumasu()
    def _raw_string_hash_(self):
        start_hash_depth = 0
        peek_char = self._tokenizer.peek(start_hash_depth)
        while peek_char == "#":
            start_hash_depth += 1
            peek_char = self._tokenizer.peek(start_hash_depth)
        if start_hash_depth > 0:
            self._token("#" * start_hash_depth)

        if peek_char != '"':
            self._error('malformed raw string')
        self._token('"')

        inside_raw_str = ""
        while True:
            peek_char = self._tokenizer.peek(len(inside_raw_str))
            if peek_char is None:
                self._token(inside_raw_str)
                self._error("EOF while reading raw string")
                continue  # This is only to satisfy the type-checker
            elif peek_char != '"':
                inside_raw_str += peek_char
                continue

            sub_inside_raw_str = '"'
            end_hash_depth = 0
            while True:
                peek_char = self._tokenizer.peek(len(inside_raw_str) + len(sub_inside_raw_str))
                if peek_char != "#":
                    break
                sub_inside_raw_str += "#"
                end_hash_depth += 1

            if end_hash_depth < start_hash_depth:
                inside_raw_str += sub_inside_raw_str
                continue

            self._token(inside_raw_str)
            self._token('"')
            if end_hash_depth > 0:
                self._token("#" * end_hash_depth)

            if end_hash_depth == start_hash_depth:
                return
            else:
                self._error("too many # characters when closing raw string")

    @tatsumasu()
    def _raw_string_quotes_(self):
        self._error("total parsing failure")


class KDLParserSemanticActions(BaseKdlSemantics):
    def bare_identifier(self, ast):
        bare = "".join(ast)
        if bare in ("true", "false", "null"):
            raise tatsu.exceptions.FailedSemantics(f"Illegal bare identifier {bare!r}.")
        return bare

    def raw_string_hash(self, ast):
        if len(ast) == 3:
            return ast[1]
        elif len(ast) == 5:
            return ast[2]

        raise tatsu.exceptions.FailedSemantics(f"Invalid raw string {ast!r}.")

    def decimal(self, ast):
        flat_value = _strflatten(ast["decimal"])
        dict.__setitem__(ast, "decimal", flat_value)
        return ast

    def hex(self, ast):
        flat_value = _strflatten(ast["hex"])
        dict.__setitem__(ast, "hex", flat_value)
        return ast

    def octal(self, ast):
        flat_value = _strflatten(ast["octal"])
        dict.__setitem__(ast, "octal", flat_value)
        return ast

    def binary(self, ast):
        flat_value = _strflatten(ast["binary"])
        dict.__setitem__(ast, "binary", flat_value)
        return ast


ast_parser = KDLParser(whitespace="", semantics=KDLParserSemanticActions(), parseinfo=False)

exists: Callable[[AST, str], bool] = (
    lambda ast, name: ast is not None and name in ast and ast[name] is not None
)

_blank = object()


def _make_decoder(
    _null_factory: NullFactory,
    _bool_factory: BoolFactory,
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
            return ast["bare"]

        return parse_string(ast["string"])

    def parse_value(ast: AST, /) -> Any:
        val = ast["value"]
        val_type: Optional[str] = None
        if exists(ast, "type"):
            val_type = parse_identifier(ast["type"])

        fallback_factory: Callable[[str], Any]
        if exists(val, "null"):
            raw_value = val["null"]
            sanitised_value = raw_value
            retval = _null_factory(val_type, sanitised_value)
            fallback_factory = lambda x: None
        elif exists(val, "boolean"):
            raw_value = val["boolean"]
            sanitised_value = raw_value
            retval = _bool_factory(val_type, sanitised_value)
            fallback_factory = lambda x: x == "true"
        elif exists(val, "hex"):
            raw_value = val["hex"]
            sanitised_value = _clean_nondecimal_number(raw_value)
            retval = _int_factory(val_type, sanitised_value, 16)
            fallback_factory = partial(int, base=16)
        elif exists(val, "octal"):
            raw_value = val["octal"]
            sanitised_value = _clean_nondecimal_number(raw_value)
            retval = _int_factory(val_type, sanitised_value, 8)
            fallback_factory = partial(int, base=8)
        elif exists(val, "binary"):
            raw_value = val["binary"]
            sanitised_value = _clean_nondecimal_number(raw_value)
            retval = _int_factory(val_type, sanitised_value, 2)
            fallback_factory = partial(int, base=2)
        elif exists(val, "decimal"):
            raw_value = val["decimal"]
            sanitised_value = raw_value.replace("_", "")
            if "." in sanitised_value or "e" in sanitised_value or "E" in sanitised_value:
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

        if retval is not _blank:
            return retval

        if val_type is None or _ignore_unknown_types:
            return fallback_factory(sanitised_value)

        if val_type is not None:
            raise KDLDecodeError(f"Failed to decode value {raw_value!r} with type {val_type!r}.")
        else:
            raise KDLDecodeError(f"Failed to decode value {raw_value!r}.")

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
        # TODO: Figure out why empty documents are so strangely handled
        if ast[0] == [None]:
            return []
        elif (
            isinstance(ast[0], list)
            and len(ast[0]) > 0
            and (
                isinstance(ast[0][0], str)
                or (isinstance(ast[0][0], tuple) and len(ast[0][0]) > 0 and ast[0][0][0] == "//")
            )
        ):
            return []

        nodes = map(parse_node, ast)
        return list(filter(None, nodes))

    return parse_nodes


def default_null_parser(val_type: FactoryTypeParam, val: str) -> Any:
    if val_type is None and val == "null":
        return None

    return _blank


def default_bool_parser(val_type: FactoryTypeParam, val: str) -> Any:
    if val_type is None:
        if val == "true":
            return True
        elif val == "false":
            return False

    return _blank


def default_int_parser(val_type: FactoryTypeParam, val: str, base: int) -> Any:
    if val_type is None:
        return int(val, base=base)

    int_val_types = ("i8", "i16", "i32", "i64")
    uint_val_types = ("u8", "u16", "u32", "u64")
    size_val_types = ("isize", "usize")

    if val_type in int_val_types or val_type in uint_val_types or val_type in size_val_types:
        return int(val, base=base)

    return _blank


def default_float_parser(val_type: FactoryTypeParam, val: str) -> Any:
    float_val_types = ("f32", "f64")
    decimal_val_types = ("decimal64", "decimal128")

    if val_type is None:
        return float(val)

    if val_type in float_val_types:
        return float(val)
    elif val_type in decimal_val_types:
        from decimal import Decimal

        return Decimal(val)

    return _blank


def default_str_parser(val_type: FactoryTypeParam, val: str) -> Any:
    if val_type is None:
        return val

    if val_type == "base64":
        from base64 import b64decode

        return b64decode(val, validate=True)
    elif val_type == "date-time" or val_type == "datetime":
        from datetime import datetime

        return datetime.fromisoformat(val)
    elif val_type == "date":
        from datetime import date

        return date.fromisoformat(val)
    elif val_type == "time":
        from datetime import time

        return time.fromisoformat(val)
    elif val_type == "decimal":
        from decimal import Decimal

        return Decimal(val)
    elif val_type == "ipv4":
        from ipaddress import IPv4Address

        return IPv4Address(val)
    elif val_type == "ipv6":
        from ipaddress import IPv6Address

        return IPv6Address(val)
    elif val_type == "regex":
        from re import compile as re_compile

        return re_compile(val)
    elif val_type == "url":
        from urllib.parse import urlparse

        return urlparse(val)
    elif val_type == "uuid":
        from uuid import UUID

        return UUID(val)

    return _blank


class KDLDecoder:
    def __init__(
        self,
        *,
        parse_null: Optional[NullFactory] = None,
        parse_bool: Optional[BoolFactory] = None,
        parse_int: Optional[IntFactory] = None,
        parse_float: Optional[FloatFactory] = None,
        parse_str: Optional[StrFactory] = None,
        ignore_unknown_types: bool = False,
    ):
        self.parse_null: NullFactory = parse_null or default_null_parser
        self.parse_bool: BoolFactory = parse_bool or default_bool_parser
        self.parse_int: IntFactory = parse_int or default_int_parser
        self.parse_float: FloatFactory = parse_float or default_float_parser
        self.parse_str: StrFactory = parse_str or default_str_parser
        self.ignore_unknown_types = ignore_unknown_types

    def decode(self, s: str, /) -> Document:
        try:
            ast = ast_parser.parse(s)
        except tatsu.exceptions.ParseException as e:
            raise KDLDecodeError("Failed to parse the document.") from e

        decoder = _make_decoder(
            self.parse_null,
            self.parse_bool,
            self.parse_int,
            self.parse_float,
            self.parse_str,
            self.ignore_unknown_types,
        )

        return Document(NodeList(decoder(ast)))


__all__ = (
    "KDLDecoder",
    "NullFactory",
    "BoolFactory",
    "IntFactory",
    "FloatFactory",
    "StrFactory",
    "default_null_parser",
    "default_bool_parser",
    "default_int_parser",
    "default_float_parser",
    "default_str_parser",
)
