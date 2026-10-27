from sly import Lexer


class NeoLexer(Lexer):
    tokens = {ID, INT, MOVE, TURN, LEFT, RIGHT, NUMBER, BOOL, TRUE, FALSE, EQ, NE, GE, LE, AND, OR, OBSTACLE, GOAL}
    literals = {'(', ')', ';', '=', '+', '-', '*', '/', '<', '>', '!'}
    ignore = ' \t'

    #Multi-character operators
    LE = r'<='
    GE = r'>='
    EQ = r'=='
    NE = r'!='
    AND = r'&&'
    OR = r'\|\|'

    ID = r'[a-zA-Z_][a-zA-Z0-9_]*'
    ID['int'] = INT
    ID['bool'] = BOOL
    ID['move'] = MOVE
    ID['turn'] = TURN
    ID['LEFT'] = LEFT
    ID['RIGHT'] = RIGHT
    ID['true'] = TRUE
    ID['false'] = FALSE
    ID['obstacle'] = OBSTACLE
    ID['goal'] = GOAL


    @_(r'\d+')
    def NUMBER(self, t):
        t.value = int(t.value)
        return t

    @_(r'//[^\n]*')
    def COMMENT(self, t):
        pass

    @_(r'\n+')
    def newline(self, t):
        self.lineno += t.value.count('\n')

    def error(self, t):
        raise ValueError(
            f"Lexical error in line {self.lineno}: "
            f"unrecognized character {t.value[0]!r}"
        )