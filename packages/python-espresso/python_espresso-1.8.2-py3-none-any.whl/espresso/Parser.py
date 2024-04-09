from enum import Enum, auto
from typing import Union, List, NamedTuple

import random

import pprint 

from .utils import Stack
from .Lexer import TokenType, Token

from .exceptions import EspressoInvalidSyntax


class StackFrame(NamedTuple):
    func_chain: List[str]
    func_params: List[Union[int, str, "StackFrame"]]

    def __str__(self):
        func_params_str = ", ".join(str(param) for param in self.func_params)
        return "{}({})".format(".".join(self.func_chain), func_params_str)



class Parser:
    def __init__(self):
        self.call_stack = Stack()
        self.tokens = None

    def next_token(self, i):
        if i + 1 >= len(self.tokens):
            return None
        return self.tokens[i + 1]

    def parse_call_chain(self, at: int, tokens) -> tuple[List[Token], int]:
        # NOTE: don't know why commenting this out works, but it does
        # assert tokens[at].type == TokenType.IDENTIFIER

        call_chain_tokens = [tokens[at]]
        offset = 0

        i = at
        while (i < len(tokens) - 1) and (tokens[i].type not in {TokenType.LPAREN, TokenType.COMMA}):
            cur, nxt = tokens[i], self.next_token(i)
            if cur.type == TokenType.DOT:
                if nxt is None or nxt.type != TokenType.IDENTIFIER:
                    raise EspressoInvalidSyntax(
                        "Invalid syntax at col {}".format(cur.position)
                    )

                offset += 2
                call_chain_tokens.append(nxt)
            i += 1


        return call_chain_tokens, offset

    def get_closing_paren_index(self, tokens, idx):
        stack = Stack()

        for i in range(idx, len(tokens)):
            if tokens[i].type == TokenType.RPAREN:
                if stack.length == 1:
                    return i
                else:
                    stack.pop()
            elif tokens[i].type == TokenType.LPAREN:
                stack.push(True)

        return None

    def parse_func_params(self, at: int, tokens) -> List[Token]:
        # NOTE: Dont know why, but removing this works? Otherwise, expression like
        #     foo(bar, baz)
        # isnt parsed correctly
        # assert tokens[at].type == TokenType.IDENTIFIER

        offset = 0

        if at+1 >= len(tokens) or tokens[at + 1].type != TokenType.LPAREN:
            return [], offset

        closing_paren_index = self.get_closing_paren_index(tokens, at + 1)

        if not closing_paren_index:
            raise EspressoInvalidSyntax(
                "( Was never closed at {}".format(tokens[at + 1].position)
            )

        func_param_tokens = tokens[at + 2 : closing_paren_index]

        resolved_params = self.parse(func_param_tokens)
        offset = closing_paren_index - at

        return resolved_params, offset

    def parse(self, tokens: List[Token]) -> Stack:
        self.tokens = tokens
        stack = Stack()

        i = 0
        while i < len(tokens):
            cur, nxt = tokens[i], self.next_token(i)

            if cur.type == TokenType.IDENTIFIER:
                call_chain_tokens, offset = self.parse_call_chain(i, tokens)
                call_chain = [tkn.value for tkn in call_chain_tokens]
                i += offset

                arguments, offset = self.parse_func_params(i, self.tokens)

                i += offset

                stack.push(StackFrame(call_chain, arguments))
            elif cur.type in {TokenType.STRING, TokenType.INTEGER}:
                stack.push(
                    cur.value if cur.type == TokenType.STRING else int(cur.value)
                )

            i += 1

        return stack
