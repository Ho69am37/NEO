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
    def __init__(self):
        raise NotImplementedError(
            "NeoParser has not been implemented yet."
        )


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