import re

import pytest

from cuddle import KDLDecodeError, loads


def test_unclosed_braces():
    errmsg = "^" + re.escape("Failed to parse the document.") + "$"
    with pytest.raises(KDLDecodeError, match=errmsg):
        loads("{")


@pytest.mark.parametrize(
    "s",
    (
        "true",
        "false",
        "null",
        "true 123",
        "false 456",
        "null 789",
    ),
)
def test_keyword_node_names(s: str):
    errmsg = "^" + re.escape("Failed to parse the document.") + "$"

    with pytest.raises(KDLDecodeError, match=errmsg):
        loads(s)
