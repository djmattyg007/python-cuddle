from cuddle import Symbol, loads


def test_empty():
    doc = loads("")
    assert len(doc) == 0
    assert str(doc) == ""


def test_bare_empty():
    doc = loads("bare")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 0
    assert str(doc) == "bare\n"


def test_bare_int_arg():
    doc = loads("bare 123")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123
    assert str(doc) == "bare 123\n"


def test_bare_float_arg():
    doc = loads("bare 123.5")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123.5
    assert str(doc) == "bare 123.5\n"


def test_bare_binary_arg():
    doc = loads("bare 0b1010")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0b1010
    assert str(doc) == "bare 10\n"


def test_bare_octal_arg():
    doc = loads("bare 0o1237")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0o1237
    assert str(doc) == "bare 671\n"


def test_bare_hex_arg():
    doc = loads("bare 0xdeadbeef")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0xDEADBEEF
    assert str(doc) == "bare 3735928559\n"


def test_bare_int_us_arg():
    doc = loads("bare 12_3")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123
    assert str(doc) == "bare 123\n"


def test_bare_float_us_arg():
    doc = loads("bare 12_3.5")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123.5
    assert str(doc) == "bare 123.5\n"


def test_bare_binary_us_arg():
    doc = loads("bare 0b1_010")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0b1010
    assert str(doc) == "bare 10\n"


def test_bare_octal_us_arg():
    doc = loads("bare 0o12_37")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0o1237
    assert str(doc) == "bare 671\n"


def test_bare_hex_us_arg():
    doc = loads("bare 0xdead_beef")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0xDEADBEEF
    assert str(doc) == "bare 3735928559\n"


def test_bare_true_arg():
    doc = loads("bare true")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] is True
    assert str(doc) == "bare true\n"


def test_bare_false_arg():
    doc = loads("bare false")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] is False
    assert str(doc) == "bare false\n"


def test_bare_null_arg():
    doc = loads("bare null")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] is None
    assert str(doc) == "bare null\n"


def test_bare_string_symbol():
    doc = loads('bare :"name goes here"')
    assert len(doc) == 1
    assert doc[0][0] == Symbol("name goes here")
    assert str(doc) == 'bare :"name goes here"\n'


def test_bare_raw_string_symbol():
    doc = loads('bare :r#"name\\goes\\here"#')
    assert len(doc) == 1
    assert doc[0][0] == Symbol("name\\goes\\here")
    assert str(doc) == 'bare :r#"name\\goes\\here"#\n'


def test_bare_deep_raw_string_symbol():
    doc = loads('bare :r####"name\\goes\\here"####')
    assert len(doc) == 1
    assert doc[0][0] == Symbol("name\\goes\\here")
    assert str(doc) == 'bare :r#"name\\goes\\here"#\n'


def test_bare_plain_symbol():
    assert str(loads("bare :foo")) == "bare :foo\n"
    assert str(loads('bare :"foo"')) == "bare :foo\n"
    assert str(loads('bare :r#"foo"#')) == "bare :foo\n"


def test_symbol_comparison():
    assert loads("bare :foo")[0][0] == Symbol("foo")
    assert loads("bare :foo")[0][0] == "foo"
    assert loads("bare :foo")[0][0] != Symbol("bar")
    assert loads("bare :foo")[0][0] != "bar"


def test_commented_empty():
    doc = loads("/-bare")
    assert len(doc) == 0
    assert str(doc) == ""


def test_commented_args():
    doc = loads('/-bare 1234 "foo"')
    assert len(doc) == 0
    assert str(doc) == ""


def test_commented_with_children():
    doc = loads("/-bare { }")
    assert len(doc) == 0
    assert str(doc) == ""


def test_children():
    doc = loads("bare { foo; bar; baz; }")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 3
    assert node.children[0].name == "foo"
    assert node.children[1].name == "bar"
    assert node.children[2].name == "baz"
    assert (
        str(doc)
        == """bare {
  foo
  bar
  baz
}
"""
    )


def test_commented_child():
    doc = loads("bare { foo; /-bar; baz; }")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 2
    assert node.children[0].name == "foo"
    assert node.children[1].name == "baz"
    assert (
        str(doc)
        == """bare {
  foo
  baz
}
"""
    )


def test_prop():
    doc = loads('bare foo="bar"')
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node["foo"] == "bar"
    assert str(doc) == 'bare foo="bar"\n'


def test_string_name():
    doc = loads('"name goes here"')
    assert len(doc) == 1
    assert doc[0].name == "name goes here"
    assert str(doc) == '"name goes here"\n'


def test_raw_string_name():
    doc = loads('r#"name\\goes\\here"#')
    assert len(doc) == 1
    assert doc[0].name == "name\\goes\\here"
    assert str(doc) == 'r#"name\\goes\\here"#\n'


def test_deep_raw_string_name():
    doc = loads('r####"name\\goes\\here"####')
    assert len(doc) == 1
    assert doc[0].name == "name\\goes\\here"
    assert str(doc) == 'r#"name\\goes\\here"#\n'


def test_plain_ident():
    assert str(loads('"foo"')) == "foo\n"
    assert str(loads('r#"foo"#')) == "foo\n"


def test_unicode_ws():
    assert str(loads("foo\u3000:bar")) == "foo :bar\n"
    assert str(loads("foo　:bar")) == "foo :bar\n"


def test_unicode_ident():
    assert str(loads("ノード")) == "ノード\n"


def test_unicode_prop_ident():
    assert str(loads("foo お名前=5")) == "foo お名前=5\n"


def test_unicode_string():
    assert str(loads('foo "☜(ﾟヮﾟ☜)"')) == 'foo "☜(ﾟヮﾟ☜)"\n'


def test_unicode():
    assert str(loads('ノード　お名前="☜(ﾟヮﾟ☜)"')) == 'ノード お名前="☜(ﾟヮﾟ☜)"\n'


def test_short_identifier():
    assert str(loads("T")) == "T\n"


def test_messy_identifiers():
    assert str(loads("struct :Mod")) == "struct :Mod\n"
    assert (
        str(loads("stringref<uint32>[:numFiles] :Files")) == "stringref<uint32>[:numFiles] :Files\n"
    )
    assert (
        str(loads("Placeable[:numPlaceables] :Placeables"))
        == "Placeable[:numPlaceables] :Placeables\n"
    )
    assert str(loads("foo :obj:stringTable[:index...]")) == "foo :obj:stringTable[:index...]\n"


def test_empty_children():
    doc = loads("foo { }")
    assert len(doc[0].children) == 0
    assert str(doc) == "foo\n"

    doc = loads("foo {}")
    assert len(doc[0].children) == 0
    assert str(doc) == "foo\n"
