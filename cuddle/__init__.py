from __future__ import annotations

from functools import partial
from os import PathLike
from typing import IO, Optional, Union

from .decoder import FloatFactory, IntFactory, KDLDecodeError, KDLDecoder, StrFactory
from .encoder import DefaultHandler, KDLEncoder, extended_default
from .structure import Document, Node, NodeList


def dumps(
    doc: Document,
    /,
    *,
    cls=None,
    indent: Union[str, int, None] = None,
    default: Optional[DefaultHandler] = None,
) -> str:
    if cls is None:
        cls = KDLEncoder

    encoder = cls(indent=indent, default=default)
    return encoder.encode(doc)


def dump(
    doc: Document,
    fp: Union[IO[str], PathLike],
    /,
    *,
    cls=None,
    indent: Union[str, int, None] = None,
    default: Optional[DefaultHandler] = None,
) -> None:
    if cls is None:
        cls = KDLEncoder

    encoder = cls(indent=indent, default=default)
    iterable = encoder.iterencode(doc)

    if isinstance(fp, PathLike):
        with open(fp, mode="w", encoding="utf-8") as f:
            for chunk in iterable:
                f.write(chunk)
    else:
        for chunk in iterable:
            fp.write(chunk)


def loads(
    s: Union[str, bytes],
    /,
    *,
    cls=None,
    parse_int: Optional[IntFactory] = None,
    parse_float: Optional[FloatFactory] = None,
    parse_str: Optional[StrFactory] = None,
    ignore_unknown_types: bool = False,
) -> Document:
    if isinstance(s, bytes):
        s = s.decode("utf-8")

    if cls is None:
        cls = KDLDecoder

    decoder = cls(
        parse_int=parse_int,
        parse_float=parse_float,
        parse_str=parse_str,
        ignore_unknown_types=ignore_unknown_types,
    )
    return decoder.decode(s)


def load(
    fp: Union[IO[str], PathLike],
    /,
    *,
    cls=None,
    parse_int: Optional[IntFactory] = None,
    parse_float: Optional[FloatFactory] = None,
    parse_str: Optional[StrFactory] = None,
    ignore_unknown_types: bool = False,
) -> Document:
    _loads = partial(
        loads,
        cls=cls,
        parse_int=parse_int,
        parse_float=parse_float,
        parse_str=parse_str,
        ignore_unknown_types=ignore_unknown_types,
    )

    if isinstance(fp, PathLike):
        with open(fp, mode="r", encoding="utf-8") as f:
            return _loads(f.read())
    else:
        return _loads(fp.read())


plain_str_parser: StrFactory = lambda _, x: x


__all__ = (
    "dump",
    "dumps",
    "load",
    "loads",
    "plain_str_parser",
    "KDLDecoder",
    "KDLDecodeError",
    "KDLEncoder",
    "extended_default",
    "Document",
    "Node",
    "NodeList",
)
