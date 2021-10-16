from io import StringIO

from cuddle import Document, KDLDecoder, KDLEncoder, Node, NodeList, dump, dumps, load, loads


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


class CustomKDLDecoder(KDLDecoder):
    pass


def test_load_custom_cls():
    doc_file = StringIO("node")
    doc = load(doc_file, cls=CustomKDLDecoder)
    assert isinstance(doc, Document)
    assert len(doc.nodes) == 1
    assert doc.nodes[0].name == "node"


def test_loads_custom_cls():
    doc_str = "node"
    doc = loads(doc_str, cls=CustomKDLDecoder)
    assert isinstance(doc, Document)
    assert len(doc.nodes) == 1
    assert doc.nodes[0].name == "node"


class CustomKDLEncoder(KDLEncoder):
    def iterencode(self, doc: Document):
        iterencoder = super().iterencode(doc)
        for chunk in iterencoder:
            yield chunk
        yield "\n"


def test_dump_custom_cls():
    doc_file = StringIO()
    doc = Document(NodeList([Node("node", None)]))
    dump(doc, doc_file, cls=CustomKDLEncoder)

    assert doc_file.getvalue() == "node\n\n"


def test_dumps_custom_cls():
    doc = Document(NodeList([Node("node", None)]))
    doc_str = dumps(doc, cls=CustomKDLEncoder)

    assert doc_str == "node\n\n"
