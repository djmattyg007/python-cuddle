from __future__ import annotations

from typing import Iterable, List, Union


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
    def __init__(self, name: str, arguments, properties, children: NodeList):
        self.name = name
        self.arguments = arguments
        self.properties = properties
        self.children = children

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

    def __getattr__(self, name: str):
        return self.properties[name]

    def __getitem__(self, name: Union[int, str]):
        if isinstance(name, int):
            return self.arguments[name]
        else:
            return self.properties[name]


class TypedNode(Node):
    def __init__(self, name: str, node_type: str, arguments, properties, children: NodeList):
        super().__init__(name, arguments, properties, children)
        self.node_type = node_type


class NodeList:
    def __init__(self, nodes: List[Node]):
        self.nodes = nodes

    def __len__(self) -> int:
        return len(self.nodes)

    def __iter__(self) -> Iterable[Node]:
        return iter(self.nodes)

    def __getitem__(self, idx: int) -> Node:
        return self.nodes[idx]


class Document:
    def __init__(self, nodes: NodeList):
        self.nodes = nodes

    def __iter__(self) -> Iterable[Node]:
        return iter(self.nodes)
