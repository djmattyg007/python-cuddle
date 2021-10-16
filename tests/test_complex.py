from pathlib import Path

from cuddle import dump, dumps, load, loads


fixtures_path = Path(__file__).parent


def test_from_path():
    before_formatting_file = fixtures_path / "complex.kdl"
    after_formatting_file = fixtures_path / "complex_formatted.kdl"

    doc = load(before_formatting_file)
    formatted_doc = after_formatting_file.read_text()

    dumped_doc = dumps(doc)
    assert dumped_doc == formatted_doc

    reloaded_doc = loads(dumped_doc)
    redumped_doc = dumps(reloaded_doc)
    assert redumped_doc == dumped_doc


def test_from_file(tmp_path: Path):
    before_formatting_file = fixtures_path / "complex.kdl"
    after_formatting_file = fixtures_path / "complex_formatted.kdl"

    with before_formatting_file.open(mode="r", encoding="utf-8") as f:
        doc = load(f)
    formatted_doc = after_formatting_file.read_text()

    dumped_doc_file = tmp_path / "output.kdl"
    with dumped_doc_file.open(mode="w", encoding="utf-8") as f:
        dump(doc, f)
    dumped_doc = dumped_doc_file.read_text()
    assert dumped_doc == formatted_doc

    with dumped_doc_file.open(mode="r", encoding="utf-8") as f:
        reloaded_doc = load(f)
    redumped_doc_file = tmp_path / "output2.kdl"
    dump(reloaded_doc, redumped_doc_file)
    redumped_doc = redumped_doc_file.read_text()
    assert redumped_doc == dumped_doc
