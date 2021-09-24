from typing import Any, Callable, Optional

import tatsu.exceptions

from ._escaping import named_escapes
from .grammar import KdlParser
from .structure import Document, Node, Symbol


TypeFactory = Callable[[str], Any]

ast_parser = KdlParser(whitespace="", parseinfo=False)

exists = lambda ast, name: ast is not None and name in ast and ast[name] is not None


class KDLDecodeError(ValueError):
    pass


class KDLDecoder:
    def __init__(
        self, *,
        parse_int: Optional[TypeFactory] = None,
        parse_float: Optional[TypeFactory] = None,
    ):
        self.parse_int = parse_int or int
        self.parse_float = parse_float or float

    def decode(self, s: str) -> Document:
        try:
            ast = ast_parser.parse(s)
        except tatsu.exceptions.ParseException as e:
            raise KDLDecodeError("Failed to parse the document.") from e

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
        props = {}
        args = []
        children = []
        if exists(ast, "props_and_args"):
            props, args = self._parse_props_and_args(ast["props_and_args"])
        if exists(ast, "children") and not exists(ast["children"], "commented"):
            children = self._parse_nodes(ast["children"]["children"])
        return Node(name, props, args, children)

    def _parse_identifier(self, ast) -> str:
        if exists(ast, "bare"):
            return "".join(ast["bare"])
        return self._parse_string(ast["string"])

    def _parse_props_and_args(self, ast):
        props = {}
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
            return Symbol(v)
        elif exists(ast, "boolean"):
            return ast["boolean"] == "true"
        elif exists(ast, "null"):
            return None

        raise KDLDecodeError(f"Unknown AST node! Internal failure: {ast!r}")

    def _parse_string(self, ast):
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
