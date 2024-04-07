from espresso.Lexer import Lexer, TokenType
from espresso.exceptions import EspressoInvalidSyntax

import pytest

lexer = Lexer()

def test_should_lex_integers():
    tokens = lexer.lex("123")
    assert tokens == [(TokenType.INTEGER, "123", 0)]

def test_should_lex_strings():
    tokens = lexer.lex('"hello"')
    assert tokens == [(TokenType.STRING, "hello", 0)]

def test_should_throw_error_on_unclosed_dquotes():
    with pytest.raises(EspressoInvalidSyntax) as exc_info:
        lexer.lex('"unclosed')

def test_should_parse_function_call_chains():
    tokens = lexer.lex("foo.bar.baz()")
    expected_tokens = [
        (TokenType.IDENTIFIER, "foo", 0),
        (TokenType.DOT, ".", 3),
        (TokenType.IDENTIFIER, "bar", 4),
        (TokenType.DOT, ".", 7),
        (TokenType.IDENTIFIER, "baz", 8),
        (TokenType.LPAREN, "(", 11),
        (TokenType.RPAREN, ")", 12)
    ]
    assert tokens == expected_tokens
