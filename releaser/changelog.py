"""A changelog AST parser"""

import io
from collections import namedtuple

WHITESPACE = " "
HASH = "#"
OPEN_BRACE = "["
CLOSE_BRACE = "]"
OPEN_PAREN = "("
CLOSE_PAREN = ")"
DASH = "-"
WORD = "word"
LINE_END = "\n"

Token = namedtuple("Token", ["token_type", "value"])

class EOFException(Exception):
    pass

class Lexer:
    def __init__(self, content):
        self.reader = io.StringIO(content)

    def _peek(self):
        pos = self.reader.tell()
        char = self._read(1)
        self.reader.seek(pos, io.SEEK_SET)
        return char

    def _read(self, num):
        value = self.reader.read(num)
        if len(value) < num:
            raise EOFException()
        return value

    def _read_match(self, match, invert=False):
        start = self.reader.tell()
        end = self.reader.tell()
        if invert:
            while self._read(1) not in match:
                end = self.reader.tell()
        else:
            while self._read(1) in match:
                end = self.reader.tell()
        self.reader.seek(start, io.SEEK_SET)
        if start < end:
            return self._read(end - start)

    def _read_whitespace(self):
        return self._read_match(" \t")

    def _read_heading(self):
        return self._read_match("#")

    def _read_line_end(self):
        line_end = self._read(1)
        if line_end == "\r" and self._peek() == "\n":
            line_end += self._read(1)
        elif line_end == "\n" and self._peek() == "\r":
            line_end += self._read(1)
        return line_end

    def __iter__(self):
        return self

    def __next__(self):
        try:
            if self._peek() in " \t":
                return Token(token_type=WHITESPACE, value=self._read_whitespace())
            if self._peek() == "#":
                return Token(token_type=HASH, value=self._read_heading())
            if self._peek() == "[":
                return Token(token_type=OPEN_BRACE, value=self._read(1))
            if self._peek() == "]":
                return Token(token_type=CLOSE_BRACE, value=self._read(1))
            if self._peek() == "(":
                return Token(token_type=OPEN_PAREN, value=self._read(1))
            if self._peek() == ")":
                return Token(token_type=CLOSE_PAREN, value=self._read(1))
            if self._peek() == "-":
                return Token(token_type=DASH, value=self._read(1))
            if self._peek() in "\r\n":
                return Token(token_type=LINE_END, value=self._read_line_end())
            return Token(token_type=WORD, value=self._read_match(" \t#[]()\r\n", invert=True))
        except EOFException:
            raise StopIteration()

changelog = """
# v1.0 Release Notes

## Release Overview

- High level items interesting about this release

## [v1.0.0] - 2024-01

### Added

- Features that have been added
- [#pr_number](link_to_pr) PR description

### Changed

- Changed behavior
- [#pr_number](link_to_pr) PR description

### Fixed

- Bug fixes
- [#pr_number](link_to_pr) PR description

### Removed

- Features that have been removed
- [#pr_number](link_to_pr) PR description
"""
lexer = Lexer(changelog)
for token in lexer:
    print(token)

