import re
from datetime import date, datetime, time
from decimal import Decimal
from ipaddress import IPv4Address, IPv6Address
from urllib.parse import ParseResult as UrlParseResult
from uuid import UUID

import pytest

from cuddle import Document, KDLDecodeError, Node, NodeList, dumps, loads, plain_str_parser


def _check_lens(node: Node, /, *, arg_count=0, prop_count=0, child_count=0) -> None:
    assert len(node.arguments) == arg_count
    assert len(node.properties) == prop_count
    assert len(node.children) == child_count


@pytest.mark.parametrize(
    "str_type",
    (
        "base64",
        "date-time",
        "datetime",
        "date",
        "time",
        "decimal",
        "ipv4",
        "ipv6",
        "regex",
        "url",
        "uuid",
    ),
)
def test_decoding_plain_str(str_type: str):
    doc = loads(f'node ({str_type})"abcdef"', parse_str=plain_str_parser)
    assert isinstance(doc, Document)
    assert len(doc.nodes) == 1
    node = doc.nodes[0]
    assert node.name == "node"
    _check_lens(node, arg_count=1)
    assert node[0] == "abcdef"


def test_encoding_bytes():
    val = b"abc123def456"
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (base64)"YWJjMTIzZGVmNDU2"\n'


def test_decoding_bytes():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == b"abc123def456"

    raw = 'node (base64)"YWJjMTIzZGVmNDU2"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_datetime():
    val = datetime(year=2021, month=10, day=3, hour=13, minute=46, second=4)
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (date-time)"2021-10-03T13:46:04"\n'


def test_decoding_datetime():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == datetime(year=2021, month=10, day=3, hour=13, minute=46, second=4)

    raw1 = 'node (date-time)"2021-10-03T13:46:04"'
    _run(raw1)
    _run(raw1 + "\n")

    raw2 = raw1.replace("date-time", "datetime")
    _run(raw2)
    _run(raw2 + "\n")


def test_encoding_date():
    val = date(year=2022, month=2, day=24)
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (date)"2022-02-24"\n'


def test_decoding_date():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == date(year=2022, month=2, day=24)

    raw = 'node (date)"2022-02-24"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_time():
    val = time(hour=14, minute=39, second=15)
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (time)"14:39:15"\n'


def test_decoding_time():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == time(hour=14, minute=39, second=15)

    raw = 'node (time)"14:39:15"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_decimal():
    val = Decimal("1234.567890")
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (decimal)"1234.567890"\n'


def test_decoding_decimal():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == Decimal("1234.567890")

    raw = 'node (decimal)"1234.567890"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_ipv4address():
    val = IPv4Address("127.0.0.1")
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (ipv4)"127.0.0.1"\n'


def test_decoding_ipv4address():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == IPv4Address("127.0.0.1")

    raw = 'node (ipv4)"127.0.0.1"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_ipv6address():
    val = IPv6Address("::1")
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (ipv6)"::1"\n'


def test_decoding_ipv6address():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == IPv6Address("::1")

    raw = 'node (ipv6)"::1"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_re():
    val = re.compile(r"^abcd$")
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (regex)"^abcd$"\n'


def test_decoding_re():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == re.compile(r"^abcd$")

    raw = 'node (regex)"^abcd$"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_url():
    val = UrlParseResult("https", "example.com", "/path/to/document", "", "", "")
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (url)"https://example.com/path/to/document"\n'


def test_decoding_url():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == UrlParseResult("https", "example.com", "/path/to/document", "", "", "")

    raw = 'node (url)"https://example.com/path/to/document"'
    _run(raw)
    _run(raw + "\n")


def test_encoding_uuid():
    val = UUID("deadbeef-dead-beef-abcd-1234deadbeef")
    doc = Document(NodeList([Node("node", None, arguments=[val])]))

    assert dumps(doc) == 'node (uuid)"deadbeef-dead-beef-abcd-1234deadbeef"\n'


def test_decoding_uuid():
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert node[0] == UUID("deadbeef-dead-beef-abcd-1234deadbeef")

    raw = 'node (uuid)"deadbeef-dead-beef-abcd-1234deadbeef"'
    _run(raw)
    _run(raw + "\n")


@pytest.mark.parametrize(
    "int_type", ("i8", "i16", "i32", "i64", "u8", "u16", "u32", "u64", "isize", "usize")
)
def test_decoding_integer(int_type: str):
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert isinstance(node[0], int)
        assert node[0] == 42

    raw = f"node ({int_type})42"
    _run(raw)
    _run(raw + "\n")


def test_decoding_invalid_integer():
    errmsg = "^" + re.escape("Failed to decode value '36' with type 'bool'.") + "$"
    with pytest.raises(KDLDecodeError, match=errmsg):
        loads("node (bool)36")


@pytest.mark.parametrize("float_type", ("f32", "f64"))
def test_decoding_float(float_type: str):
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert isinstance(node[0], float)
        assert node[0] == 1.23

    raw = f"node ({float_type})1.23"
    _run(raw)
    _run(raw + "\n")


def test_decoding_invalid_float():
    errmsg = "^" + re.escape("Failed to decode value '3.142' with type 'bool'.") + "$"
    with pytest.raises(KDLDecodeError, match=errmsg):
        loads("node (bool)3.142")


@pytest.mark.parametrize("decimal_type", ("decimal64", "decimal128"))
def test_decoding_floatdecimal(decimal_type: str):
    def _run(_raw: str):
        doc = loads(_raw)
        assert len(doc.nodes) == 1
        node = doc.nodes[0]
        assert node.name == "node"
        _check_lens(node, arg_count=1)
        assert isinstance(node[0], Decimal)
        assert str(node[0]) == "0.0000123"

    raw = f"node ({decimal_type})1.23E-5"
    _run(raw)
    _run(raw + "\n")
