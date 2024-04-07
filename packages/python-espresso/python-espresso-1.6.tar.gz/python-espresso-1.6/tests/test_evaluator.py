from espresso import Evaluator, Lexer, Parser, exceptions
from espresso.Evaluator import Func

import pytest

evaluator = Evaluator()

p = lambda src: Parser().parse(Lexer().lex(src))

def test_should_parse_simple_expression():
    evaluator.define_function(Func(lambda x, y: x + y, ["add"], ["int", "int"])) 
    result = evaluator.eval(p("add(1, 2)"))
    assert result == 3

def test_should_handle_errors():
    with pytest.raises(exceptions.EspressoNameError):
        evaluator.eval(p("foo(333)"))

    with pytest.raises(exceptions.EspressoNameError):
        evaluator.eval(p("foo.bar.baz(1000)"))

def test_should_check_type_system():
    evaluator.define_function(Func(
        lambda x: x, ["foo"], ["str"]
    ))

    with pytest.raises(exceptions.EspressoTypeError):
        evaluator.eval(p("foo(32)"))

    with pytest.raises(exceptions.EspressoTypeError):
        evaluator.eval(p('foo("bar", "baz")'))


    with pytest.raises(exceptions.EspressoNameError):
        evaluator.define_function(Func(lambda x: x * x, ["square"], ["unknown type"]))
    
