#!/usr/bin/env python3
"""codedigest.py - a digest of a script's code without its comments and docstrings, so that a copy whose comments were
cleaned can be shown to hold the same code as the script that ran (CL-3's notes v3, question 5, option (a), decided by
the operator on 2026-10-11).

    python codedigest.py FILE [FILE ...]     prints "codedigest:<hex>  FILE" for each

Python (.py): the file's tokens, as Python's own tokenizer reads them, less comments, blank-line and encoding tokens and
the docstrings (a string that is the first statement of the module, a class or a function, found with the ast module);
each remaining token written as its type name and its text, one per line.
JavaScript (.js): the text less its comments (// to the line's end, and /* to */), read by a scanner that skips string
literals ('...', "...", `...`) and regular-expression literals (a / where an operand cannot end); then every run of
whitespace written as one space, and the ends trimmed.
The digest is the SHA-256 of that text, encoded as UTF-8. It depends on nothing but the file and the Python standard
library. What it shows: two files with the same digest differ at most in comments, docstrings and layout.
"""
from __future__ import annotations

import ast
import hashlib
import io
import re
import sys
import tokenize
from pathlib import Path

SKIP = {tokenize.COMMENT, tokenize.NL, tokenize.ENCODING}


def python_text(source: str) -> str:
    tree = ast.parse(source)
    spans = set()
    for node in ast.walk(tree):
        if isinstance(node, (ast.Module, ast.ClassDef, ast.FunctionDef, ast.AsyncFunctionDef)) and node.body:
            first = node.body[0]
            if isinstance(first, ast.Expr) and isinstance(first.value, ast.Constant) and isinstance(first.value.value, str):
                spans.add((first.lineno, first.col_offset))
    out = []
    for tok in tokenize.generate_tokens(io.StringIO(source).readline):
        if tok.type in SKIP:
            continue
        if tok.type == tokenize.STRING and tok.start in spans:
            continue
        out.append(f"{tokenize.tok_name[tok.type]} {tok.string}")
    return "\n".join(out)


REGEX_AFTER = set("(,=:[!&|?{};+-*%<>~^")


def js_text(source: str) -> str:
    out, i, n, last = [], 0, len(source), ""
    while i < n:
        c = source[i]
        if source.startswith("//", i):
            i = source.find("\n", i)
            i = n if i < 0 else i
            continue
        if source.startswith("/*", i):
            j = source.find("*/", i + 2)
            if j < 0:
                raise ValueError("an unclosed /* comment")
            i = j + 2
            out.append(" ")
            continue
        if c in "'\"`":
            j = i + 1
            while j < n and source[j] != c:
                j += 2 if source[j] == "\\" else 1
            out.append(source[i:j + 1])
            last, i = c, j + 1
            continue
        if c == "/" and (last == "" or last in REGEX_AFTER or re.search(r"\b(return|typeof|case|in|of)\s*$",
                                                                         "".join(out)[-12:])):
            j, cls = i + 1, False
            while j < n and (source[j] != "/" or cls):
                if source[j] == "\\":
                    j += 1
                elif source[j] == "[":
                    cls = True
                elif source[j] == "]":
                    cls = False
                j += 1
            j += 1
            while j < n and source[j].isalpha():
                j += 1
            out.append(source[i:j])
            last, i = "/", j
            continue
        out.append(c)
        if not c.isspace():
            last = c
        i += 1
    return re.sub(r"\s+", " ", "".join(out)).strip()


def digest(path: Path, data: bytes | None = None) -> str:
    text = (path.read_bytes() if data is None else data).decode("utf-8").replace("\r\n", "\n")
    body = python_text(text) if path.suffix == ".py" else js_text(text) if path.suffix == ".js" else None
    if body is None:
        raise ValueError(f"{path.name}: only .py and .js are read")
    return "codedigest:" + hashlib.sha256(body.encode("utf-8")).hexdigest()


if __name__ == "__main__":
    for arg in sys.argv[1:]:
        print(f"{digest(Path(arg))}  {arg}")
