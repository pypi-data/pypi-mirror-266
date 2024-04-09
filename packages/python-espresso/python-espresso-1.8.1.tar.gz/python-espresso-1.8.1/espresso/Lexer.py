from enum import Enum, auto
from typing import NamedTuple

from .exceptions import EspressoInvalidSyntax


class TokenType(Enum):
    LPAREN = auto()
    RPAREN = auto()
    DOT = auto()

    INTEGER = auto()
    STRING = auto()
    IDENTIFIER = auto()


class Token(NamedTuple):
    type: TokenType
    value: str
    position: int


class Lexer:
    def __init__(self):
        self.input = None
        self.cursor = -1

    def lex(self, input_string):
        self.input = input_string.strip().replace("\n", " ")
        self.cursor = -1

        tokens = []

        while self.advance() is not None:
            if self.cur() == ".":
                tokens.append(Token(TokenType.DOT, ".", self.cursor))
            elif (
                self.cur() == ","
            ):  # TODO: ignoring commas is problematic because the in func calls any delimeter can be used unless specified otherwise
                pass
            elif self.cur() == "(":
                tokens.append(Token(TokenType.LPAREN, "(", self.cursor))
            elif self.cur() == ")":
                tokens.append(Token(TokenType.RPAREN, ")", self.cursor))
            elif self.cur() == '"':
                n = self.find_next_index('"')
                
                if n is None:
                    raise EspressoInvalidSyntax(
                        f"Unterminated string literal at position {self.cursor}"
                    )
                tokens.append(
                    Token(
                        TokenType.STRING, self.input[self.cursor + 1 : n], self.cursor
                    )
                )
                self.cursor = n
            elif self.cur() == " ":
                continue
            elif self.cur().isdigit():
                start = self.cursor
                end = self.cursor
                while end < len(self.input) and self.input[end].isdigit():
                    end += 1
                tokens.append(Token(TokenType.INTEGER, self.input[start:end], start))
                self.cursor = end - 1
            elif self.cur().isalpha():
                start = self.cursor
                end = self.cursor
                while end < len(self.input) and self.input[end].isalpha():
                    end += 1
                tokens.append(Token(TokenType.IDENTIFIER, self.input[start:end], start))
                self.cursor = end - 1
            else:
                raise EspressoInvalidSyntax(
                    f"Invalid character encountered at position {self.cursor}: {self.cur()}"
                )

        return tokens

    def cur(self):
        if self.cursor >= len(self.input):
            return None
        return self.input[self.cursor]

    def find_next_index(self, char):
        for i in range(self.cursor + 1, len(self.input)):
            if self.input[i] == char:
                return i
        return None

    def retreat(self):
        if self.cursor == 0:
            return None

        self.cursor -= 1
        return self.cursor

    def advance(self):
        if self.cursor == (len(self.input) - 1):
            return None

        self.cursor += 1
        return self.cursor
