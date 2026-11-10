from sly import Parser

from compiler.lexer import NeoLexer
from compiler.ast_nodes import (
    Program, VarDeclaration, Assignment, Move, Turn,
    Number, Boolean, Variable, BinaryOp, UnaryOp, Sensor, If, Block, While, FunctionCall, FunctionDefinition
)
from compiler.symbol_table import SymbolTable, SemanticError


class NeoParser(Parser):
    tokens = NeoLexer.tokens

    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()
        self.current_return_type = None

    def parse(self, tokens):
        self.symbol_table.clear()
        self.current_return_type = None
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

    def check_condition(self, cond, keyword):
        if cond.type != 'bool':
            raise SemanticError(
                f"The condition of '{keyword}' must be bool, got {cond.type}"
            )

    def check_call(self, name, args):
        """Common checks for a call: function exists, arguments match."""
        func = self.symbol_table.lookup_function(name)
        if len(args) != len(func.param_types):
            raise SemanticError(
                f"Function '{name}' expects {len(func.param_types)} "
                f"argument(s), got {len(args)}"
            )
        for i, (arg, expected) in enumerate(zip(args, func.param_types), 1):
            if arg.type != expected:
                raise SemanticError(
                    f"Argument {i} of '{name}' must be {expected}, "
                    f"got {arg.type}"
                )
        return func

    def check_main(self):
        try:
            main = self.symbol_table.lookup_function("main")
        except SemanticError:
            raise SemanticError("The program must define 'void main()'")
        if main.return_type != 'void' or main.param_types:
            raise SemanticError(
                "Invalid main() signature: it must be 'void main()' "
                "with no parameters"
            )
    # ---- program ----
    @_('function_list')
    def program(self, p):
        self.check_call(self)
        return Program(p.function_list)

    @_('function_list function')
    def function_list(self, p):
        return p.function_list + [p.function]

    @_('function')
    def function_list(self, p):
        return [p.function]

    @_('return_type ID "(" param_list_opt ")"')
    def function_header(self, p):
        param_type = [q.type for q in p.param_list_opt ]
        self.symbol_table.insert_function(p.ID, p.return_type, param_type)
        self.symbol_table.push_scope()
        for q in p.param_list_opt:
            self.symbol_table.insert(q.name, q.type)
        self.current_return_type = p.return_type
        return (p.ID, p.return_type, p.param_list_opt) 

    @_('function_header "{" statement_list "}"')
    def function(self, p):
        name, return_type, params = p.function_header
        self.symbol_table.pop_scope()
        self.current_return_type = None
        return FunctionDefinition(name, return_type, params, Block(p.statement_list))
    
    @_('declaration')
    def top_statement(self, p):
        return p.declaration

    @_('statement')
    def top_statement(self, p):
        return p.statement

    # ---- statements ----
    @_('INT ID ";"')
    def declaration(self, p):
        self.symbol_table.insert(p.ID, "int")
        return VarDeclaration(p.ID, "int")

    @_('BOOL ID ";"')
    def declaration(self, p):
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

    @_('IF "(" expr ")" block')
    def statement(self, p):
        self.check_condition(p.expr, 'if')
        return If(p.expr, p.block)

    @_('IF "(" expr ")" block ELSE block')
    def statement(self, p):
        self.check_condition(p.expr, 'if')
        return If(p.expr, p.block0, p.block1)

    @_('WHILE "(" expr ")" block')
    def statement(self, p):
        self.check_condition(p.expr, 'while')
        return While(p.expr, p.block)

    # ---- Block rules -----
    @_('"{" block_body "}"')
    def block(self, p):
        return  Block(p.block_body)

    @_('block_body statement')
    def block_body(self, p):
        return p.block_body + [p.statement]

    @_('statement')
    def block_body(self, p):
        return [p.statement]

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