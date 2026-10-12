from sly import Parser

from compiler.lexer import NeoLexer
from compiler.ast_nodes import Program, Move, Turn


class NeoParser(Parser):
    """
    Syntax analyzer for the Neo language.

    Practice 1:
    Implement this class using SLY's Parser class.

    The parser must recognize the Neo P1 grammar and construct
    an AST using Program, Move and Turn nodes.
    """
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

    @_('MOVE "(" NUMBER ")" ";"') 
    def statement(self, p):
        return Move(p.NUMBER)

    @_('TURN "(" LEFT ")" ";"')
    def statement(self, p):
        return Turn("LEFT")

    @_('TURN "(" RIGHT ")" ";"')
    def statement(self, p):
        return Turn("RIGHT")

    def error(self, p):
        if p:
            raise SyntaxError(
                f"Syntax error at line {p.lineno}: "
                f"unexpected token {p.value!r}"
            )
        else:
            raise SyntaxError("Syntax error at EOF")
# ---------------------------------------------------------
# TODO
# ---------------------------------------------------------
#
# Replace the provisional NeoParser class above with a
# syntax analyzer based on:
#
#     class NeoParser(Parser):
#
# The parser must:
#
#   - use the tokens produced by NeoLexer
#   - recognize complete Neo programs
#   - recognize sequences of statements
#   - recognize the statements supported by Neo P1
#   - construct the corresponding AST
#
# Syntax errors must be reported by raising SyntaxError.
#
# ---------------------------------------------------------