# python-cuddle

A Python library for the [KDL Document Language](https://github.com/kdl-org/kdl).

## Install

    pip install cuddle

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
doc = Document(NodeList([]))
nodes = []
child_node = Node("complex name here!", [], {}, NodeList([]))
nodes.append(
    Node("simple-name", [123], {}, NodeList([child_node]))
)
node_list = NodeList(nodes)
doc = Document(node_list)
print(dumps(doc))
```

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
```

## License

The code is available under the [MIT license](LICENSE). The example above is
made available from https://github.com/kdl-org/kdl under
[Creative Commons Attribution-ShareAlike 4.0 International](https://github.com/kdl-org/kdl/blob/main/LICENSE.md).
