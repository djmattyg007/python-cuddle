from pathlib import Path

from collections import OrderedDict
from .grammar import KdlParser
import regex, sys

model = KdlParser(whitespace="", parseinfo=False)

named_escapes = {
    "\\": "\\",
    "/": "/",
    "r": "\r",
    "n": "\n",
    "t": "\t",
    '"': '"',
    "b": "\b",
    "f": "\f",
}
named_escape_inverse = {v: k for k, v in named_escapes.items()}

exists = lambda ast, name: ast is not None and name in ast and ast[name] is not None

identRe = regex.compile(
    r'^[^\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$'
)


def format_identifier(ident):
    if identRe.match(ident):
        return ident
    else:
        return format_string(ident)


def format_string(val):
    if "\\" in val and '"' not in val:
        return 'r#"%s"#' % val
    return '"%s"' % "".join(
        "\\" + named_escape_inverse[c] if c in named_escape_inverse else c for c in val
    )


def format_value(val):
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


class Document(list):
    def __init__(
        self, document=None, preserve_property_order=False, symbols_as_strings=False
    ):
        list.__init__(self)
        if document is not None:
            parse(document, preserve_property_order, symbols_as_strings, dlist=self)

    def __str__(self):
        return "\n".join(map(str, self))


class Node(object):
    def __init__(self, name, properties, arguments, children):
        self.name = name
        self.properties = properties
        self.arguments = arguments
        self.children = children

    def __str__(self):
        return self.format()

    def format(self, indent=False):
        fmt = format_identifier(self.name)
        if self.properties:
            for k, v in self.properties.items():
                fmt += " %s=%s" % (format_identifier(k), format_value(v))
        if self.arguments:
            for v in self.arguments:
                fmt += " " + format_value(v)
        if self.children:
            fmt += " {\n"
            for child in self.children:
                fmt += child.format(indent=True) + "\n"
            fmt += "}"
        return "\n".join("\t" + line for line in fmt.split("\n")) if indent else fmt

    def __repr__(self):
        return "Node(name=%r%s%s%s)" % (
            self.name,
            ", properties=%r" % self.properties if self.properties else "",
            ", arguments=%r" % self.arguments if self.arguments else "",
            ", children=%r" % self.children if self.children else "",
        )

    def items(self):
        return self.properties.items() if self.properties else ()

    def __iter__(self):
        if self.properties:
            for prop in self.properties.items():
                yield prop
        if self.arguments:
            for arg in self.arguments:
                yield arg
        if self.children:
            for child in self.children:
                yield child

    def __getattr__(self, name):
        return self[name]

    def __getitem__(self, name):
        if isinstance(name, int):
            return self.arguments[name]
        else:
            return self.properties[name]


class Symbol(object):
    def __init__(self, value):
        self.value = value

    def __repr__(self):
        return "Symbol(%r)" % self.value

    def __str__(self):
        return ":%s" % self.value

    def __eq__(self, right):
        return (
            isinstance(right, Symbol) and right.value == self.value
        ) or self.value == right

    def __ne__(self, right):
        return not (self == right)


class Parser(object):
    def __init__(self, document, preserve_property_order, symbols_as_strings, dlist):
        self.preserve_property_order = preserve_property_order
        self.symbols_as_strings = symbols_as_strings

        if isinstance(document, Path):
            document = document.read_text(encoding="utf-8")
        elif hasattr(document, "read") and callable(document.read):
            document = document.read()

        if isinstance(document, bytes):
            document = document.decode("utf-8")
        ast = model.parse(document)

        self.document = Document() if dlist is None else dlist
        self.document += self.parse_nodes(ast)

    def parse_nodes(self, ast):
        if ast[0] == [None] or (
            isinstance(ast[0], list)
            and len(ast[0]) > 0
            and isinstance(ast[0][0], str)
        ):
            # TODO: Figure out why empty documents are so strangely handled
            return []

        nodes = map(self.parse_node, ast)
        return [node for node in nodes if node is not None]

    def parse_node(self, ast):
        if len(ast) == 0 or exists(ast, "commented"):
            return

        name = self.parse_identifier(ast["name"])
        children = props = args = None
        if exists(ast, "props_and_args"):
            props, args = self.parse_props_and_args(ast["props_and_args"])
        if exists(ast, "children") and not exists(ast["children"], "commented"):
            children = self.parse_nodes(ast["children"]["children"])
        return Node(name, props, args, children)

    def parse_identifier(self, ast):
        if exists(ast, "bare"):
            return "".join(ast["bare"])
        return self.parse_string(ast["string"])

    def parse_props_and_args(self, ast):
        props = OrderedDict() if self.preserve_property_order else {}
        args = []
        for elem in ast:
            if exists(elem, "commented"):
                continue
            if exists(elem, "prop"):
                props[self.parse_identifier(elem["prop"]["name"])] = self.parse_value(
                    elem["prop"]["value"]
                )
            else:
                args.append(self.parse_value(elem["value"]))
        return props if len(props) else None, args if len(args) else None

    def parse_value(self, ast):
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
            return self.parse_string(ast)
        elif exists(ast, "symbol"):
            v = self.parse_identifier(ast["symbol"])
            if self.symbols_as_strings:
                return v
            return Symbol(v)
        elif exists(ast, "boolean"):
            return ast["boolean"] == "true"
        elif exists(ast, "null"):
            return None
        raise "Unknown AST node! Internal failure: %r" % ast

    def parse_string(self, ast):
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


def parse(
    document, preserve_property_order=False, symbols_as_strings=False, dlist=None
):
    parser = Parser(document, preserve_property_order, symbols_as_strings, dlist)
    return parser.document
