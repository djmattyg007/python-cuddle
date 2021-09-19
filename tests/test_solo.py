from cuddle import Symbol, parse


def test_empty():
    doc = parse("")
    assert len(doc) == 0
    assert str(doc) == ""


def test_bare_empty():
    doc = parse("bare")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 0
    assert str(doc) == "bare"


def test_bare_int_arg():
    doc = parse("bare 123")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123
    assert str(doc) == "bare 123"


def test_bare_float_arg():
    doc = parse("bare 123.5")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123.5
    assert str(doc) == "bare 123.5"


def test_bare_binary_arg():
    doc = parse("bare 0b1010")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0b1010
    assert str(doc) == "bare 10"


def test_bare_octal_arg():
    doc = parse("bare 0o1237")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0o1237
    assert str(doc) == "bare 671"


def test_bare_hex_arg():
    doc = parse("bare 0xdeadbeef")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0xDEADBEEF
    assert str(doc) == "bare 3735928559"


def test_bare_int_us_arg():
    doc = parse("bare 12_3")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123
    assert str(doc) == "bare 123"


def test_bare_float_us_arg():
    doc = parse("bare 12_3.5")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 123.5
    assert str(doc) == "bare 123.5"


def test_bare_binary_us_arg():
    doc = parse("bare 0b1_010")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0b1010
    assert str(doc) == "bare 10"


def test_bare_octal_us_arg():
    doc = parse("bare 0o12_37")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0o1237
    assert str(doc) == "bare 671"


def test_bare_hex_us_arg():
    doc = parse("bare 0xdead_beef")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] == 0xDEADBEEF
    assert str(doc) == "bare 3735928559"


def test_bare_true_arg():
    doc = parse("bare true")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] is True
    assert str(doc) == "bare true"


def test_bare_false_arg():
    doc = parse("bare false")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] is False
    assert str(doc) == "bare false"


def test_bare_null_arg():
    doc = parse("bare null")
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node[0] is None
    assert str(doc) == "bare null"


def test_bare_string_symbol():
    doc = parse('bare :"name goes here"')
    assert len(doc) == 1
    assert doc[0][0] == Symbol("name goes here")
    assert str(doc) == 'bare :"name goes here"'


def test_bare_raw_string_symbol():
    doc = parse('bare :r#"name\\goes\\here"#')
    assert len(doc) == 1
    assert doc[0][0] == Symbol("name\\goes\\here")
    assert str(doc) == 'bare :r#"name\\goes\\here"#'


def test_bare_deep_raw_string_symbol():
    doc = parse('bare :r####"name\\goes\\here"####')
    assert len(doc) == 1
    assert doc[0][0] == Symbol("name\\goes\\here")
    assert str(doc) == 'bare :r#"name\\goes\\here"#'


def test_bare_plain_symbol():
    assert str(parse("bare :foo") == "bare :foo")
    assert str(parse('bare :"foo"') == "bare :foo")
    assert str(parse('bare :r#"foo"#') == "bare :foo")


def test_symbol_comparison():
    assert parse("bare :foo")[0][0] == Symbol("foo")
    assert parse("bare :foo")[0][0] == "foo"
    assert parse("bare :foo")[0][0] != Symbol("bar")
    assert parse("bare :foo")[0][0] != "bar"


def test_commented_empty():
    doc = parse("/-bare")
    assert len(doc) == 0
    assert str(doc) == ""


def test_commented_args():
    doc = parse('/-bare 1234 "foo"')
    assert len(doc) == 0
    assert str(doc) == ""


def test_commented_with_children():
    doc = parse("/-bare { }")
    assert len(doc) == 0
    assert str(doc) == ""


def test_children():
    doc = parse("bare { foo; bar; baz; }")
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
}"""
    )


def test_commented_child():
    doc = parse("bare { foo; /-bar; baz; }")
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
}"""
    )


def test_prop():
    doc = parse('bare foo="bar"')
    assert len(doc) == 1
    node = doc[0]
    assert node.name == "bare"
    assert len(list(node)) == 1
    assert node["foo"] == "bar"
    assert str(doc) == 'bare foo="bar"'


def test_string_name():
    doc = parse('"name goes here"')
    assert len(doc) == 1
    assert doc[0].name == "name goes here"
    assert str(doc) == '"name goes here"'


def test_raw_string_name():
    doc = parse('r#"name\\goes\\here"#')
    assert len(doc) == 1
    assert doc[0].name == "name\\goes\\here"
    assert str(doc) == 'r#"name\\goes\\here"#'


def test_deep_raw_string_name():
    doc = parse('r####"name\\goes\\here"####')
    assert len(doc) == 1
    assert doc[0].name == "name\\goes\\here"
    assert str(doc) == 'r#"name\\goes\\here"#'


def test_plain_ident():
    assert str(parse('"foo"')) == "foo"
    assert str(parse('r#"foo"#')) == "foo"


def test_unicode_ws():
    assert str(parse("foo\u3000:bar")) == "foo :bar"
    assert str(parse("foo　:bar")) == "foo :bar"


def test_unicode_ident():
    assert str(parse("ノード")) == "ノード"


def test_unicode_prop_ident():
    assert str(parse("foo お名前=5")) == "foo お名前=5"


def test_unicode_string():
    assert str(parse('foo "☜(ﾟヮﾟ☜)"')) == 'foo "☜(ﾟヮﾟ☜)"'


def test_unicode():
    assert str(parse('ノード　お名前="☜(ﾟヮﾟ☜)"')) == 'ノード お名前="☜(ﾟヮﾟ☜)"'


def test_short_identifier():
    assert str(parse("T") == "T")


def test_messy_identifiers():
    assert str(parse("struct :Mod")) == "struct :Mod"
    assert str(
        parse("stringref<uint32>[:numFiles] :Files") == "stringref<uint32>[:numFiles] :Files"
    )
    assert str(
        parse("Placeable[:numPlaceables] :Placeables") == "Placeable[:numPlaceables] :Placeables"
    )
    assert str(parse("foo :obj:stringTable[:index...]") == "foo :obj:stringTable[:index...]")


def test_empty_children():
    doc = parse("foo { }")
    assert len(doc[0].children) == 0
    assert str(doc) == "foo"

    doc = parse("foo {}")
    assert len(doc[0].children) == 0
    assert str(doc) == "foo"
