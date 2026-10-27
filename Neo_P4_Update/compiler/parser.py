from sly import Parser

from compiler.lexer import NeoLexer
from compiler.ast_nodes import (
    Program, VarDeclaration, Assignment, Move, Turn,
    Number, Boolean, Variable, BinaryOp, UnaryOp, Sensor
)
from compiler.symbol_table import SymbolTable, SemanticError


class NeoParser(Parser):
    tokens = NeoLexer.tokens

    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()

    def reset(self):
        self.symbol_table.clear()

    def parse(self, tokens):
        self.reset()
        return super().parse(tokens)

    # ---- semantic helpers ----
    def binary(self, op, l, r, operand_type, result_type):
        if l.type != operand_type or r.type != operand_type:
            raise SemanticError(
                f"Operator '{op}' requires {operand_type} operands, "
                f"got {l.type} and {r.type}"
            )
        return BinaryOp(op, l, r, result_type)

    def equality_op(self, op, l, r):
        if l.type != r.type:
            raise SemanticError(
                f"Operator '{op}' requires operands of the same type, "
                f"got {l.type} and {r.type}"
            )
        return BinaryOp(op, l, r, 'bool')

    def unary_op(self, op, operand, operand_type):
        if operand.type != operand_type:
            raise SemanticError(
                f"Operator '{op}' requires a {operand_type} operand, "
                f"got {operand.type}"
            )
        return UnaryOp(op, operand, operand_type)

    # ---- program ----
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
        self.symbol_table.insert(p.ID, "int")
        return VarDeclaration(p.ID, "int")

    @_('BOOL ID ";"')
    def statement(self, p):
        self.symbol_table.insert(p.ID, "bool")
        return VarDeclaration(p.ID, "bool")

    @_('ID "=" expr ";"')
    def statement(self, p):
        var_type = self.symbol_table.lookup(p.ID)
        if var_type != p.expr.type:
            raise SemanticError(
                f"Cannot assign {p.expr.type} to variable "
                f"'{p.ID}' of type {var_type}"
            )
        return Assignment(p.ID, p.expr)

    @_('MOVE "(" expr ")" ";"')
    def statement(self, p):
        if p.expr.type != 'int':
            raise SemanticError(f"move() requires an int, got {p.expr.type}")
        return Move(p.expr)

    @_('TURN "(" LEFT ")" ";"')
    def statement(self, p):
        return Turn("LEFT")

    @_('TURN "(" RIGHT ")" ";"')
    def statement(self, p):
        return Turn("RIGHT")

    # ---- expressions (lowest -> highest precedence) ----
    @_('logical_or')
    def expr(self, p):
        return p.logical_or

    @_('logical_or OR logical_and')
    def logical_or(self, p):
        return self.binary("||", p.logical_or, p.logical_and, 'bool', 'bool')

    @_('logical_and')
    def logical_or(self, p):
        return p.logical_and

    @_('logical_and AND equality')
    def logical_and(self, p):
        return self.binary("&&", p.logical_and, p.equality, 'bool', 'bool')

    @_('equality')
    def logical_and(self, p):
        return p.equality

    @_('equality EQ relational')
    def equality(self, p):
        return self.equality_op("==", p.equality, p.relational)

    @_('equality NE relational')
    def equality(self, p):
        return self.equality_op("!=", p.equality, p.relational)

    @_('relational')
    def equality(self, p):
        return p.relational

    @_('relational "<" additive')
    def relational(self, p):
        return self.binary("<", p.relational, p.additive, 'int', 'bool')

    @_('relational LE additive')
    def relational(self, p):
        return self.binary("<=", p.relational, p.additive, 'int', 'bool')

    @_('relational ">" additive')
    def relational(self, p):
        return self.binary(">", p.relational, p.additive, 'int', 'bool')

    @_('relational GE additive')
    def relational(self, p):
        return self.binary(">=", p.relational, p.additive, 'int', 'bool')

    @_('additive')
    def relational(self, p):
        return p.additive

    @_('additive "+" term')
    def additive(self, p):
        return self.binary("+", p.additive, p.term, 'int', 'int')

    @_('additive "-" term')
    def additive(self, p):
        return self.binary("-", p.additive, p.term, 'int', 'int')

    @_('term')
    def additive(self, p):
        return p.term

    @_('term "*" unary')
    def term(self, p):
        return self.binary("*", p.term, p.unary, 'int', 'int')

    @_('term "/" unary')
    def term(self, p):
        return self.binary("/", p.term, p.unary, 'int', 'int')

    @_('unary')
    def term(self, p):
        return p.unary

    @_('"-" unary')
    def unary(self, p):
        return self.unary_op("-", p.unary, 'int')

    @_('"!" unary')
    def unary(self, p):
        return self.unary_op("!", p.unary, 'bool')

    @_('primary')
    def unary(self, p):
        return p.primary

    @_('NUMBER')
    def primary(self, p):
        return Number(p.NUMBER, 'int')

    @_('TRUE')
    def primary(self, p):
        return Boolean(True, 'bool')

    @_('FALSE')
    def primary(self, p):
        return Boolean(False, 'bool')

    @_('ID')
    def primary(self, p):
        var_type = self.symbol_table.lookup(p.ID)
        return Variable(p.ID, var_type)

    @_('OBSTACLE "(" ")"')
    def primary(self, p):
        return Sensor("obstacle", 'bool')

    @_('GOAL "(" ")"')
    def primary(self, p):
        return Sensor("goal", 'bool')

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