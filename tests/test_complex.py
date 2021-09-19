import os
import sys

from cuddle import parse


def test_from_file():
    with open("complex.kdl", "r") as fp:
        doc = parse(fp)
    if sys.version_info.major == 3:
        with open("complex_formatted.kdl", "r", encoding="utf-8") as fp:
            assert fp.read() == str(doc)
    else:
        with open("complex_formatted.kdl", "r") as fp:
            assert fp.read().decode("utf-8") == str(doc)
