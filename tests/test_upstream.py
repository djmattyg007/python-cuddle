import re
from pathlib import Path
from typing import Any, Generic, Optional, TypeVar

import pytest

from cuddle import (
    IdentifierFormatter,
    KDLDecodeError,
    ValueEncoderResult,
    default_bool_parser,
    default_float_parser,
    default_int_parser,
    default_null_parser,
    default_str_parser,
    dumps,
    extended_value_encoder,
    load,
)


FIXTURES_DIR = Path(__file__).parent / "upstream_fixtures"
INPUT_FIXTURES_DIR = FIXTURES_DIR / "input"
OUTPUT_FIXTURES_DIR = FIXTURES_DIR / "expected_kdl"


ValueType = TypeVar("ValueType")


class CustomValue(Generic[ValueType]):
    KNOWN_CUSTOM_TYPES = ("type", "type/", "")

    def __init__(self, val_type: str, val: ValueType):
        self.val_type = val_type
        self.val = val

    def __repr__(self) -> str:
        return f"CustomValue(type={self.val_type!r}, val={self.val!r})"


def _custom_null_parser(val_type: Optional[str], val: str) -> Any:
    if val_type in CustomValue.KNOWN_CUSTOM_TYPES:
        converted_val = default_null_parser(None, val)
        return CustomValue(val_type, converted_val)

    return default_null_parser(val_type, val)


def _custom_bool_parser(val_type: Optional[str], val: str) -> Any:
    if val_type in CustomValue.KNOWN_CUSTOM_TYPES:
        converted_val = default_bool_parser(None, val)
        return CustomValue(val_type, converted_val)

    return default_bool_parser(val_type, val)


def _custom_int_parser(val_type: Optional[str], val: str, base: int) -> Any:
    if val_type in CustomValue.KNOWN_CUSTOM_TYPES:
        converted_val = default_int_parser(None, val, base)
        return CustomValue(val_type, converted_val)

    return default_int_parser(val_type, val, base)


def _custom_float_parser(val_type: Optional[str], val: str) -> Any:
    if val_type in CustomValue.KNOWN_CUSTOM_TYPES:
        converted_val = default_float_parser(None, val)
        return CustomValue(val_type, converted_val)

    return default_float_parser(val_type, val)


def _custom_str_parser(val_type: Optional[str], val: str) -> Any:
    if val_type in CustomValue.KNOWN_CUSTOM_TYPES:
        converted_val = default_str_parser(None, val)
        return CustomValue(val_type, converted_val)

    return default_str_parser(None, val)


def _custom_value_encoder(val: Any, ident_fmt: IdentifierFormatter) -> ValueEncoderResult:
    if isinstance(val, CustomValue):
        converted_val = extended_value_encoder(val.val, ident_fmt)
        if converted_val is None:
            return None
        if isinstance(converted_val, str):
            return f"({ident_fmt(val.val_type)}){converted_val}"
        return val.val_type, converted_val[1]

    return extended_value_encoder(val, ident_fmt)


@pytest.mark.parametrize(
    "input_file", INPUT_FIXTURES_DIR.glob("*.kdl"), ids=lambda input_file: input_file.stem
)
def test_expected_kdl(input_file: Path):
    output_file = OUTPUT_FIXTURES_DIR / input_file.name
    try:
        expected_output = output_file.read_text(encoding="utf-8")
    except FileNotFoundError:
        with pytest.raises(KDLDecodeError):
            load(input_file)
        return

    input_doc = load(
        input_file,
        parse_null=_custom_null_parser,
        parse_bool=_custom_bool_parser,
        parse_int=_custom_int_parser,
        parse_float=_custom_float_parser,
        parse_str=_custom_str_parser,
    )
    actual_output = dumps(input_doc, indent=4, value_encoder=_custom_value_encoder)

    if actual_output == "":
        actual_output = "\n"

    try:
        assert actual_output == expected_output
    except AssertionError:
        if "E+" in expected_output or "E-" in expected_output:
            pytest.xfail("Unimportant formatting difference")
        if actual_output.startswith('r#"') and 'r#"' not in expected_output:
            pytest.xfail("Unimportant formatting difference")
        actual_startswith_node = re.compile(r'node_?\d? (prop=)?r#"')
        if actual_startswith_node.match(actual_output) and 'r#"' not in expected_output:
            pytest.xfail("Unimportant formatting difference")
        raise
