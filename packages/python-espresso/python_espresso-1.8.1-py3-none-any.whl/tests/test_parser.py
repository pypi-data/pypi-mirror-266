from espresso.Parser import Parser, StackFrame, Stack
from espresso.Lexer import Lexer
from espresso.exceptions import EspressoInvalidSyntax

import pytest

parser = Parser()
lexer = Lexer()


def test_should_parse_simple_expression():
    stack = parser.parse(lexer.lex("foo(bar(baz()))"))

    
    top = stack.pop()
    assert isinstance(top, StackFrame)
    assert top.func_chain == ["foo"]

    top = top.func_params.pop()
    assert isinstance(top, StackFrame)
    assert top.func_chain == ["bar"]
    
    
def test_should_resolve_flat_call_stack():
    stack = parser.parse(lexer.lex("32, 33, 34, \"foo\""))

    assert stack.pop() == "foo"

    assert stack.pop() == 34
    assert stack.pop() == 33
    assert stack.pop() == 32

def test_should_resolve_nested_stack():
    stack = parser.parse(lexer.lex("foo(bar(), 123)"))

    top = stack.pop()

    assert isinstance(top, StackFrame)
    assert top.func_params.length == 2

    assert top.func_params.pop() == 123
    assert isinstance(top.func_params.pop(), StackFrame)


def test_should_rase_necessary_exceptions():
    with pytest.raises(EspressoInvalidSyntax):
        parser.parse(lexer.lex("foo(bar()"))

    with pytest.raises(EspressoInvalidSyntax):
        parser.parse(lexer.lex("foo.(bar()"))
