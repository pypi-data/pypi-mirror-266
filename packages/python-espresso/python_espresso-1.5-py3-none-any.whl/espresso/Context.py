from .Parser import Parser
from .Lexer import Lexer
from .Evaluator import Evaluator, Func


class Context:
    def __init__(self):
        self.lexer = Lexer()
        self.parser = Parser()
        self.evaluator = Evaluator()

    def define_function(self, *args):
        self.evaluator.define_function(Func(*args))

    def eval(self, src):
        return self.evaluator.eval(self.parser.parse(self.lexer.lex(src)))
