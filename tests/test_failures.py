import re

import pytest

from cuddle import KDLDecodeError, loads


def test_unclosed_braces():
    errmsg = "^" + re.escape("Failed to parse the document.") + "$"
    with pytest.raises(KDLDecodeError, match=errmsg):
        loads("{")
