import re

import pytest

from cuddle.structure import Document, Node, NodeList


def test_node_repr1():
    node = Node("node", None, arguments=[1, 2], properties={"key": "value"})
    assert repr(node) == "Node(name='node', arguments=[1, 2], properties={'key': 'value'})"


def test_node_repr2():
    node = Node("node", "type")
    assert repr(node) == "Node(name='node', type='type')"


def test_node_repr3():
    node = Node("node", None, properties={"key": "value", "prop": False})
    assert repr(node) == "Node(name='node', properties={'key': 'value', 'prop': False})"


def test_node_repr4():
    node = Node("node", "group", children=[Node("sub", None), Node("sub", None)])
    assert (
        repr(node)
        == "Node(name='node', type='group', children=[Node(name='sub'), Node(name='sub')])"
    )


def test_node_iter():
    node = Node("node", None, arguments=[1, 2, 3])

    errmsg = "^" + re.escape("KDL nodes are not iterable.") + "$"
    with pytest.raises(TypeError, match=errmsg):
        iter(node)


def test_nodelist_get_by_name():
    node1 = Node("main", None)
    node2 = Node("main", None)
    node3 = Node("other", None)

    nodelist = NodeList([node1, node2, node3])

    main_nodes = list(nodelist.get_nodes_by_name("main"))
    assert len(main_nodes) == 2

    for node in main_nodes:
        assert node.name == "main"


def test_document_repr():
    node1 = Node("main", None)
    node2 = Node("other", None)

    nodelist = NodeList([node1, node2])
    doc = Document(nodelist)

    assert repr(doc) == "Document([Node(name='main'), Node(name='other')])"
