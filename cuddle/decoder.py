from __future__ import annotations

from typing import Any, Callable, List, Optional, Sequence

import tatsu.exceptions
from tatsu.ast import AST

from ._escaping import named_escapes
from .grammar import KdlParser
from .structure import Document, Node, NodeList, TypedNode


TypeFactory = Callable[[str], Any]

ast_parser = KdlParser(whitespace="", parseinfo=False)

exists: Callable[[AST, str], bool] = (
    lambda ast, name: ast is not None and name in ast and ast[name] is not None
)


class KDLDecodeError(ValueError):
    pass


def _make_decoder(_parse_int: TypeFactory, _parse_float: TypeFactory):
    def parse_string(ast: AST):
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

    def parse_identifier(ast: AST) -> str:
        if exists(ast, "bare"):
            return "".join(ast["bare"])

        return parse_string(ast["string"])

    def parse_value(ast: AST):
        if exists(ast, "hex"):
            raw_value = ast["hex"].replace("_", "")
            return int(raw_value[0] + raw_value[3:] if raw_value[0] != "0" else raw_value[2:], 16)
        elif exists(ast, "octal"):
            raw_value = ast["octal"].replace("_", "")
            return int(raw_value[0] + raw_value[3:] if raw_value[0] != "0" else raw_value[2:], 8)
        elif exists(ast, "binary"):
            raw_value = ast["binary"].replace("_", "")
            return int(raw_value[0] + raw_value[3:] if raw_value[0] != "0" else raw_value[2:], 2)
        elif exists(ast, "decimal"):
            raw_value = ast["decimal"].replace("_", "")
            if "." in raw_value or "e" in raw_value or "E" in raw_value:
                return _parse_float(raw_value)
            else:
                return _parse_int(raw_value)
        elif exists(ast, "escstring") or exists(ast, "rawstring"):
            return parse_string(ast)
        elif exists(ast, "boolean"):
            return ast["boolean"] == "true"
        elif exists(ast, "null"):
            return None

        raise KDLDecodeError(f"Unknown AST node! Internal failure: {ast!r}")

    def parse_args_and_props(ast: Sequence[AST]):
        args = []
        props = {}
        for elem in ast:
            if exists(elem, "commented"):
                continue
            if exists(elem, "prop"):
                props[parse_identifier(elem["prop"]["name"])] = parse_value(
                    elem["prop"]["value"]["value"]
                )
            else:
                args.append(parse_value(elem["value"]["value"]))
        return props, args

    def parse_node(ast: AST) -> Optional[Node]:
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

        if exists(ast, "type"):
            node_type = parse_identifier(ast["type"])
            return TypedNode(name, node_type, args, props, NodeList(children))
        else:
            return Node(name, args, props, NodeList(children))

    def parse_nodes(ast: Sequence[AST]) -> List[Node]:
        if ast[0] == [None] or (
            isinstance(ast[0], list) and len(ast[0]) > 0 and isinstance(ast[0][0], str)
        ):
            # TODO: Figure out why empty documents are so strangely handled
            return []

        nodes = map(parse_node, ast)
        return list(filter(None, nodes))

    return parse_nodes


class KDLDecoder:
    def __init__(
        self,
        *,
        parse_int: Optional[TypeFactory] = None,
        parse_float: Optional[TypeFactory] = None,
    ):
        self.parse_int = parse_int or int
        self.parse_float = parse_float or float

    def decode(self, s: str, /) -> Document:
        try:
            ast = ast_parser.parse(s)
        except tatsu.exceptions.ParseException as e:
            raise KDLDecodeError("Failed to parse the document.") from e

        decoder = _make_decoder(self.parse_int, self.parse_float)

        return Document(NodeList(decoder(ast)))


__all__ = (
    "KDLDecoder",
    "KDLDecodeError",
)
