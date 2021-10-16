from pathlib import Path

from cuddle import dumps, load, loads


fixtures_path = Path(__file__).parent


def test_from_file():
    before_formatting_file = fixtures_path / "complex.kdl"
    after_formatting_file = fixtures_path / "complex_formatted.kdl"

    doc = load(before_formatting_file)
    formatted_doc = after_formatting_file.read_text()

    dumped_doc = dumps(doc)
    assert dumped_doc == formatted_doc

    reloaded_doc = loads(dumped_doc)
    redumped_doc = dumps(reloaded_doc)
    assert redumped_doc == dumped_doc
