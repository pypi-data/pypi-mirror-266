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


class Parser:
    def __init__(self):
        self.call_stack = Stack()
        self.tokens = None

    def next_token(self, i):
        if i + 1 >= len(self.tokens):
            return None
        return self.tokens[i + 1]

    def parse_call_chain(self, at: int) -> tuple[List[Token], int]:
        assert self.tokens[at].type == TokenType.IDENTIFIER
        call_chain_tokens = [self.tokens[at]]
        offset = 0

        i = 0
        while (i < len(self.tokens) - 1) and (self.tokens[i].type != TokenType.LPAREN):
            cur, nxt = self.tokens[i], self.next_token(i)

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

    def parse_func_params(self, at: int) -> List[Token]:
        assert self.tokens[at].type == TokenType.IDENTIFIER
        offset = 0

        if at+1 >= len(self.tokens) or self.tokens[at + 1].type != TokenType.LPAREN:
            return [], offset

        closing_paren_index = self.get_closing_paren_index(self.tokens, at + 1)

        if not closing_paren_index:
            raise EspressoInvalidSyntax(
                "( Was never closed at {}".format(self.tokens[at + 1].position)
            )

        func_param_tokens = self.tokens[at + 2 : closing_paren_index]

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
                call_chain_tokens, offset = self.parse_call_chain(i)
                call_chain = [tkn.value for tkn in call_chain_tokens]
                i += offset

                arguments, offset = self.parse_func_params(i)
                i += offset

                stack.push(StackFrame(call_chain, arguments))
            elif cur.type in {TokenType.STRING, TokenType.INTEGER}:
                stack.push(
                    cur.value if cur.type == TokenType.STRING else int(cur.value)
                )

            i += 1

        return stack
