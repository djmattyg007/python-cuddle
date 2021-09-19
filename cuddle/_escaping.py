named_escapes = {
    "\\": "\\",
    "/": "/",
    "r": "\r",
    "n": "\n",
    "t": "\t",
    '"': '"',
    "b": "\b",
    "f": "\f",
}
named_escape_inverse = {v: k for k, v in named_escapes.items()}
