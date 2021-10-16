from cuddle import Document, loads


def test_loads_bytes():
    b = b'node 1 2 3 key="value"'
    doc = loads(b)

    assert isinstance(doc, Document)
    assert len(doc.nodes) == 1
    node = doc.nodes[0]
    assert node.name == "node"
    assert len(node.arguments) == 3
    assert len(node.properties) == 1
    assert node.arguments == [1, 2, 3]
    assert node.properties["key"] == "value"
