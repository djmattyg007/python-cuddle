import re

import pytest

from cuddle import ParserError, parse


def test_unclosed_braces():
    errmsg = "^" + re.escape("Failed to parse the document.") + "$"
    with pytest.raises(ParserError, match=errmsg):
        parse("{")
