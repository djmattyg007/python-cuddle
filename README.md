# python-cuddle

[![CI](https://github.com/djmattyg007/python-cuddle/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/djmattyg007/python-cuddle/actions/workflows/ci.yml)
[![PyPI](https://img.shields.io/pypi/v/cuddle.svg)](https://pypi.org/project/cuddle)

A Python library for the [KDL Document Language](https://github.com/kdl-org/kdl).

## Install

```shell
pip install cuddle
```

Or if you're using poetry:

```shell
poetry add cuddle
```

Cuddle supports Python 3.9 and above. 

## Usage

```python
from cuddle import Document, Node, NodeList, dumps, loads

loaded_doc = loads('''// Nodes can be separated into multiple lines
title \
  "Some title"

// Nested nodes are fully supported
contents {
  section "First section" {
    paragraph "This is the first paragraph"
    paragraph "This is the second paragraph"
  }
}

// Files must be utf8 encoded!
smile "😁"

// Instead of anonymous nodes, nodes and properties can be wrapped
// in "" for arbitrary node names.
"!@#$@$%Q#$%~@!40" "1.2.3" "!!!!!"=true

// The following is a legal bare identifier:
foo123~!@#$%^&*.:'|/?+ "weeee"

// And you can also use unicode!
ノード　お名前="☜(ﾟヮﾟ☜)"

// kdl specifically allows properties and values to be
// interspersed with each other, much like CLI commands.
foo bar=true "baz" quux=false 1 2 3
''')
print(dumps(loaded_doc))

print()

# Creating documents from scratch is a bit verbose
nodes = []
child_node = Node("complex name here!", None)
nodes.append(
    Node("simple-name", None, arguments=[123], children=[child_node])
)
nodes.append(
    Node("second-node", None, properties={"key": "value"})
)
node_list = NodeList(nodes)
doc = Document(node_list)
print(dumps(doc))
```

The output:

```
title "Some title"
smile "😁"
!@#$@$%Q#$%~@!40 !!!!!=true "1.2.3"
foo123~!@#$%^&*.:'|/?+ "weeee"
ノード お名前="☜(ﾟヮﾟ☜)"
foo bar=true quux=false "baz" 1 2 3

simple-name 123 {
  "complex name here!"
}
second-node key="value"
```

## License

The code is available under the [MIT license](LICENSE.txt).
