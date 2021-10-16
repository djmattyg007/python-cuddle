from __future__ import annotations

from functools import partial
from os import PathLike
from typing import IO, Optional, Type, Union

from .decoder import (
    BoolFactory,
    FloatFactory,
    IntFactory,
    KDLDecoder,
    NullFactory,
    StrFactory,
    default_bool_parser,
    default_float_parser,
    default_int_parser,
    default_null_parser,
    default_str_parser,
)
from .encoder import (
    IdentifierFormatter,
    KDLEncoder,
    ValueEncoder,
    ValueEncoderResult,
    default_value_encoder,
    extended_value_encoder,
)
from .exception import KDLDecodeError, KDLEncodeTypeError
from .structure import Document, Node, NodeList


__version__ = "1.0.2"


def dumps(
    doc: Document,
    /,
    *,
    cls=None,
    indent: Union[str, int, None] = None,
    value_encoder: Optional[ValueEncoder] = None,
) -> str:
    if cls is None:
        cls = KDLEncoder

    encoder = cls(indent=indent, value_encoder=value_encoder)
    return encoder.encode(doc)


def dump(
    doc: Document,
    fp: Union[IO[str], PathLike],
    /,
    *,
    cls=None,
    indent: Union[str, int, None] = None,
    value_encoder: Optional[ValueEncoder] = None,
) -> None:
    if cls is None:
        cls = KDLEncoder

    encoder = cls(indent=indent, value_encoder=value_encoder)
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
    parse_null: Optional[NullFactory] = None,
    parse_bool: Optional[BoolFactory] = None,
    parse_int: Optional[IntFactory] = None,
    parse_float: Optional[FloatFactory] = None,
    parse_str: Optional[StrFactory] = None,
    ignore_unknown_types: bool = False,
    node_factory: Type[Node] = Node,
    node_list_factory: Type[NodeList] = NodeList,
) -> Document:
    if isinstance(s, bytes):
        s = s.decode("utf-8")

    if cls is None:
        cls = KDLDecoder

    decoder = cls(
        parse_null=parse_null,
        parse_bool=parse_bool,
        parse_int=parse_int,
        parse_float=parse_float,
        parse_str=parse_str,
        ignore_unknown_types=ignore_unknown_types,
        node_factory=node_factory,
        node_list_factory=node_list_factory,
    )
    return decoder.decode(s)


def load(
    fp: Union[IO[str], PathLike],
    /,
    *,
    cls=None,
    parse_null: Optional[NullFactory] = None,
    parse_bool: Optional[BoolFactory] = None,
    parse_int: Optional[IntFactory] = None,
    parse_float: Optional[FloatFactory] = None,
    parse_str: Optional[StrFactory] = None,
    ignore_unknown_types: bool = False,
    node_factory: Type[Node] = Node,
    node_list_factory: Type[NodeList] = NodeList,
) -> Document:
    _loads = partial(
        loads,
        cls=cls,
        parse_null=parse_null,
        parse_bool=parse_bool,
        parse_int=parse_int,
        parse_float=parse_float,
        parse_str=parse_str,
        ignore_unknown_types=ignore_unknown_types,
        node_factory=node_factory,
        node_list_factory=node_list_factory,
    )

    if isinstance(fp, PathLike):
        with open(fp, mode="r", encoding="utf-8") as f:
            return _loads(f.read())
    else:
        return _loads(fp.read())


plain_str_parser: StrFactory = lambda _, val: val


__all__ = (
    "dump",
    "dumps",
    "load",
    "loads",
    "KDLDecoder",
    "KDLDecodeError",
    "plain_str_parser",
    "default_null_parser",
    "default_bool_parser",
    "default_int_parser",
    "default_float_parser",
    "default_str_parser",
    "KDLEncoder",
    "KDLEncodeTypeError",
    "IdentifierFormatter",
    "ValueEncoder",
    "ValueEncoderResult",
    "default_value_encoder",
    "extended_value_encoder",
    "Document",
    "Node",
    "NodeList",
)
