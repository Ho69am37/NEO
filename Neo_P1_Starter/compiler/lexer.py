from sly import Lexer


class NeoLexer(Lexer):
    """
    Lexical analyzer for the Neo language.

    Practice 1:
    Implement this class using SLY's Lexer class so that it
    recognizes the lexical elements of the Neo P1 language.
    """
    tokens = {MOVE, TURN, RIGHT, LEFT, NUMBER}
    literals = { '(', ')', ';' }
    ignore = ' \t'

    MOVE = r'move'
    TURN = r'turn'
    RIGHT = r'RIGHT'
    LEFT = r'LEFT'
    NUMBER = r'\d+'
    

    ID = r'[a-zA-Z_]\w*'
    
    #COMMENT
    @_(r'//[^\n]*')
    def COMMENT(self, t):
        pass

    #line tracking
    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    #error handler
    def error(self, t):
        raise ValueError(
            f"Lexical error in line {self.lineno}"
            f"unrecognized character {t.value[0]!r}"
        )    

# ---------------------------------------------------------
# TODO
# ---------------------------------------------------------
#
# Replace the provisional NeoLexer class above with a
# lexical analyzer based on:
#
#     class NeoLexer(Lexer):
#
# Your implementation must define:
#
#   - the tokens required by Neo P1
#   - the literal characters
#   - ignored characters
#   - lexical rules
#   - reserved words
#   - integer constants
#   - comments
#   - line counting
#
# Lexical errors must be reported by raising ValueError.
#
# Example:
#
#     raise ValueError(
#         f"Line {self.lineno}: unrecognized character ..."
#     )
#
# ---------------------------------------------------------