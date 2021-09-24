from __future__ import annotations

from functools import partial
from os import PathLike
from typing import IO, Optional, Union

from .decoder import KDLDecoder, KDLDecodeError, TypeFactory
from .encoder import DefaultHandler, KDLEncoder, extended_default
from .structure import Document, Node, Symbol


def dumps(
    doc: Document, /, *,
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
    /, *,
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
    s: Union[str, bytes], /, *,
    cls=None,
    preserve_property_order: bool = False,
    symbols_as_strings: bool = False,
    parse_int: Optional[TypeFactory] = None,
    parse_float: Optional[TypeFactory] = None,
) -> Document:
    if isinstance(s, bytes):
        s = s.decode("utf-8")

    if cls is None:
        cls = KDLDecoder

    decoder = cls(
        preserve_property_order=preserve_property_order,
        symbols_as_strings=symbols_as_strings,
        parse_int=parse_int,
        parse_float=parse_float,
    )
    return decoder.decode(s)


def load(
    fp: Union[IO[str], PathLike],
    /, *,
    cls=None,
    preserve_property_order: bool = False,
    symbols_as_strings: bool = False,
    parse_int: Optional[TypeFactory] = None,
    parse_float: Optional[TypeFactory] = None,
) -> Document:
    _loads = partial(
        loads,
        cls=cls,
        preserve_property_order=preserve_property_order,
        symbols_as_strings=symbols_as_strings,
        parse_int=parse_int,
        parse_float=parse_float,
    )

    if isinstance(fp, PathLike):
        with open(fp, mode="r", encoding="utf-8") as f:
            return _loads(f.read())
    else:
        return _loads(fp.read())


__all__ = (
    "load",
    "loads",
    "KDLDecoder",
    "KDLDecodeError",
    "KDLEncoder",
    "extended_default",
    "Document",
    "Node",
    "Symbol",
)
