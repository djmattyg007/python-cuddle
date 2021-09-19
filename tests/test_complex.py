from pathlib import Path

from cuddle import parse


fixtures_path = Path(__file__).parent


def test_from_file():
    before_formatting_file = fixtures_path / "complex.kdl"
    after_formatting_file = fixtures_path / "complex_formatted.kdl"

    doc = parse(before_formatting_file)
    formatted_doc = after_formatting_file.read_text()

    assert str(doc).strip() == formatted_doc.strip()
