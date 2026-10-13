from sly import Lexer


class NeoLexer(Lexer):
    """
    Lexical analyzer for the Neo language.

    Practice 1:
    Implement this class using SLY's Lexer class so that it
    recognizes the lexical elements of the Neo P1 language.
    """
    tokens = {ID, INT, ASSIGN,  MOVE, TURN, RIGHT, LEFT, NUMBER, PLUS, MINUS, TIMES, DIVIDE}
    literals = { '(', ')', ';' }
    ignore = ' \t'

    #COMMENT
    @_(r'//[^\n]*')
    def COMMENT(self, t):
        pass
    
    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ASSIGN = r'='
    PLUS = r'\+'
    MINUS = r'-'
    TIMES = r'\*'
    DIVIDE = r'/'

    ID['int'] = INT 
    ID['move'] = MOVE
    ID['turn'] = TURN
    ID['RIGHT'] = RIGHT
    ID['LEFT'] = LEFT
    
    

    

    #NUMBER
    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)   #string → int
        return t
    

    #line tracking
    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    #error handler
    def error(self, t):
        raise ValueError(
            f"Lexical error in line {self.lineno}: "
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