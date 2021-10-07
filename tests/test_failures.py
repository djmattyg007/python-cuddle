import re

import pytest

from cuddle import KDLDecodeError, loads


def test_unclosed_braces():
    errmsg = "^" + re.escape("Failed to parse the document.") + "$"
    with pytest.raises(KDLDecodeError, match=errmsg):
        loads("{")


@pytest.mark.parametrize(
    ("s", "ident"),
    (
        ("true", "true"),
        ("false", "false"),
        ("null", "null"),
        ("true 123", "true"),
        ("false 456", "false"),
        ("null 789", "null"),
    ),
)
def test_keyword_node_names(s: str, ident: str):
    errmsg = "^" + re.escape(f"Illegal bare identifier '{ident}'.") + "$"

    with pytest.raises(KDLDecodeError, match=errmsg):
        loads(s)


@pytest.mark.parametrize(
    ("s", "ident"),
    (
        ("(true)node", "true"),
        ("(false)node", "false"),
        ("(null)node", "null"),
        ("node (true)123", "true"),
        ("node (false)456", "false"),
        ("node (null)789", "null"),
    ),
)
def test_keyword_type_annotations(s: str, ident: str):
    errmsg = "^" + re.escape(f"Illegal bare identifier '{ident}'.") + "$"

    with pytest.raises(KDLDecodeError, match=errmsg):
        loads(s)


def test_unknown_type():
    errmsg = "^" + re.escape("Failed to decode value 'roflcopter' with type 'unknown'.") + "$"

    with pytest.raises(KDLDecodeError, match=errmsg):
        loads('node (unknown)"roflcopter"')
