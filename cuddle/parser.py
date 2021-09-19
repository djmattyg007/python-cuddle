from __future__ import annotations

from collections import OrderedDict
from pathlib import Path

from ._escaping import named_escapes
from .grammar import KdlParser
from .structure import Document, Node, Symbol


ast_parser = KdlParser(whitespace="", parseinfo=False)

exists = lambda ast, name: ast is not None and name in ast and ast[name] is not None


class ParserError(Exception):
    pass


class Parser:
    def __init__(
        self,
        *,
        preserve_property_order: bool = False,
        symbols_as_strings: bool = False,
    ):
        self.preserve_property_order = preserve_property_order
        self.symbols_as_strings = symbols_as_strings

    def parse(self, document, /) -> Document:
        if isinstance(document, Path):
            document = document.read_text(encoding="utf-8")
        elif hasattr(document, "read") and callable(document.read):
            document = document.read()

        if isinstance(document, bytes):
            document = document.decode("utf-8")
        ast = ast_parser.parse(document)

        return Document(self._parse_nodes(ast))

    def _parse_nodes(self, ast):
        if ast[0] == [None] or (
            isinstance(ast[0], list) and len(ast[0]) > 0 and isinstance(ast[0][0], str)
        ):
            # TODO: Figure out why empty documents are so strangely handled
            return []

        nodes = map(self._parse_node, ast)
        return list(filter(None, nodes))

    def _parse_node(self, ast):
        if len(ast) == 0 or exists(ast, "commented"):
            return

        name = self._parse_identifier(ast["name"])
        props = OrderedDict() if self.preserve_property_order else {}
        args = []
        children = []
        if exists(ast, "props_and_args"):
            props, args = self.parse_props_and_args(ast["props_and_args"])
        if exists(ast, "children") and not exists(ast["children"], "commented"):
            children = self._parse_nodes(ast["children"]["children"])
        return Node(name, props, args, children)

    def _parse_identifier(self, ast) -> str:
        if exists(ast, "bare"):
            return "".join(ast["bare"])
        return self._parse_string(ast["string"])

    def parse_props_and_args(self, ast):
        props = OrderedDict() if self.preserve_property_order else {}
        args = []
        for elem in ast:
            if exists(elem, "commented"):
                continue
            if exists(elem, "prop"):
                props[self._parse_identifier(elem["prop"]["name"])] = self._parse_value(
                    elem["prop"]["value"]
                )
            else:
                args.append(self._parse_value(elem["value"]))
        return props, args

    def _parse_value(self, ast):
        if exists(ast, "hex"):
            v = ast["hex"].replace("_", "")
            return int(v[0] + v[3:] if v[0] != "0" else v[2:], 16)
        elif exists(ast, "octal"):
            v = ast["octal"].replace("_", "")
            return int(v[0] + v[3:] if v[0] != "0" else v[2:], 8)
        elif exists(ast, "binary"):
            v = ast["binary"].replace("_", "")
            return int(v[0] + v[3:] if v[0] != "0" else v[2:], 2)
        elif exists(ast, "decimal"):
            v = ast["decimal"].replace("_", "")
            if "." in v or "e" in v or "E" in v:
                return float(v)
            else:
                return int(v)
        elif exists(ast, "escstring") or exists(ast, "rawstring"):
            return self._parse_string(ast)
        elif exists(ast, "symbol"):
            v = self._parse_identifier(ast["symbol"])
            if self.symbols_as_strings:
                return v
            return Symbol(v)
        elif exists(ast, "boolean"):
            return ast["boolean"] == "true"
        elif exists(ast, "null"):
            return None

        raise ParserError(f"Unknown AST node! Internal failure: {ast!r}")

    def _parse_string(self, ast):
        if exists(ast, "escstring"):
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
        return ast["rawstring"]


def parse(document, *, preserve_property_order: bool = False, symbols_as_strings: bool = False):
    parser = Parser(
        preserve_property_order=preserve_property_order,
        symbols_as_strings=symbols_as_strings,
    )
    return parser.parse(document)


__all__ = ("Parser", "parse")
