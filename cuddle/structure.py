from typing import Sequence

import regex

from ._escaping import named_escape_inverse


ident_re = regex.compile(
    r'^[^\\<{;\[=,"0-9\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029][^\\;=,"\t \u00A0\u1680\u2000-\u200A\u202F\u205F\u3000\uFFEF\r\n\u0085\u000C\u2028\u2029]*$'
)


class Symbol:
    def __init__(self, value: str):
        self.value = value

    def __repr__(self) -> str:
        return f"Symbol({self.value})"

    def __str__(self) -> str:
        return ":" + self.value

    def __eq__(self, right) -> bool:
        return (isinstance(right, Symbol) and right.value == self.value) or self.value == right

    def __ne__(self, right) -> bool:
        return not (self == right)


class Node:
    def __init__(self, name, properties, arguments, children):
        self.name = name
        self.properties = properties
        self.arguments = arguments
        self.children: Sequence[Node] = children

    def __str__(self) -> str:
        return self.format_node()

    def format_node(self, *, indent: bool = False) -> str:
        fmt = format_identifier(self.name)

        if self.properties:
            for k, v in self.properties.items():
                fmt += " {0}={1}".format(format_identifier(k), format_value(v))

        if self.arguments:
            for v in self.arguments:
                fmt += " " + format_value(v)

        if self.children:
            fmt += " {\n"
            for child in self.children:
                fmt += child.format_node(indent=True) + "\n"
            fmt += "}"

        if not indent:
            return fmt

        return "\n".join("  " + line for line in fmt.split("\n"))

    def __repr__(self) -> str:
        details = [f"name={self.name!r}"]
        if self.properties:
            details.append(f"properties={self.properties!r}")
        if self.arguments:
            details.append(f"arguments={self.arguments!r}")
        if self.children:
            details.append(f"children={self.children!r}")
        return f"Node({', '.join(details)})"

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
        return self.properties[name]

    def __getitem__(self, name):
        if isinstance(name, int):
            return self.arguments[name]
        else:
            return self.properties[name]


class Document(list):
    def __init__(self, nodes=None):
        if nodes:
            super().__init__(nodes)
        else:
            super().__init__()

    def __str__(self):
        return "\n".join(map(str, self))


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
