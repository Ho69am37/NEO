from sly import Parser

from compiler.lexer import NeoLexer
from compiler.ast_nodes import (
    Program, VarDeclaration, Assignment, Move, Turn,
    Number, Variable, BinaryOp, UnaryOp
)


class NeoParser(Parser):
    tokens = NeoLexer.tokens

    @_('statement_list')
    def program(self, p):
        return Program(p.statement_list)

    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    # ---- statements ----
    @_('INT ID ";"')
    def statement(self, p):
        return VarDeclaration(p.ID)

    @_('ID "=" expr ";"')
    def statement(self, p):
        return Assignment(p.ID, p.expr)

    @_('MOVE "(" expr ")" ";"')
    def statement(self, p):
        return Move(p.expr)

    @_('TURN "(" LEFT ")" ";"')
    def statement(self, p):
        return Turn("LEFT")

    @_('TURN "(" RIGHT ")" ";"')
    def statement(self, p):
        return Turn("RIGHT")

    # ---- expressions ----
    @_('expr "+" term')
    def expr(self, p):
        return BinaryOp("+", p.expr, p.term)

    @_('expr "-" term')
    def expr(self, p):
        return BinaryOp("-", p.expr, p.term)

    @_('term')
    def expr(self, p):
        return p.term

    @_('term "*" unary')
    def term(self, p):
        return BinaryOp("*", p.term, p.unary)

    @_('term "/" unary')
    def term(self, p):
        return BinaryOp("/", p.term, p.unary)

    @_('unary')
    def term(self, p):
        return p.unary

    @_('"-" unary')
    def unary(self, p):
        return UnaryOp("-", p.unary)

    @_('primary')
    def unary(self, p):
        return p.primary

    @_('NUMBER')
    def primary(self, p):
        return Number(p.NUMBER)

    @_('ID')
    def primary(self, p):
        return Variable(p.ID)

    @_('"(" expr ")"')
    def primary(self, p):
        return p.expr

    def error(self, p):
        if p:
            raise SyntaxError(
                f"Syntax error at line {p.lineno}: "
                f"unexpected token {p.value!r}"
            )
        raise SyntaxError("Syntax error at EOF")