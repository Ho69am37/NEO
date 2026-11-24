from sly import Parser

from compiler.lexer import NeoLexer
from compiler.ast_nodes import (
    Program, Parameter, FunctionDefinition, FunctionCall, Return,
    VarDeclaration, Assignment, Move, Turn, Block, If, While,
    Number, Boolean, Variable, BinaryOp, UnaryOp, Sensor, ArrayDeclaration,
    ArrayAccess, ArrayAssignment
)
from compiler.symbol_table import SymbolTable, SemanticError


class NeoParser(Parser):
    tokens = NeoLexer.tokens
    def __init__(self):
        super().__init__()
        self.symbol_table = SymbolTable()
        self.current_return_type = None   # return type of the function being parsed
        self.memory_layouts = {}
        self.local_counter = 0
        self.layout_entries = []

    def parse(self, tokens):
        self.symbol_table.clear()
        self.current_return_type = None
        self.memory_layouts = {}
        self.local_counter = 0
        self.layout_entries = []
        return super().parse(tokens)
    

    # ---------------- semantic helpers ----------------
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

    def get_array(self, name):
            sym = self.symbol_table.lookup_symbol(name)
            if sym.kind != "array":
                raise SemanticError(f"'{name}' is not an array and cannot be indexed.")
            return sym
    
    def check_index(self, index):
        if index.type != 'int':
            raise SemanticError(f"Array index must be int, got {index.type}")

    def allocate(self, name, type, kind, size=None):
        size_bytes = 4 if size is None else 4 * size
        self.local_counter += size_bytes
        offset = -self.local_counter                   
        entry = {
            "name": name,
            "kind": kind,
            "type": type,
            "offset": offset,
            "size_bytes": size_bytes,
        }
        if size is not None:
            entry["size"] = size
        self.layout_entries.append(entry)

    # ---------------- program and functions ----------------
    @_('function_list')
    def program(self, p):
        self.check_main()
        return Program(p.function_list)

    @_('function_list function')
    def function_list(self, p):
        return p.function_list + [p.function]

    @_('function')
    def function_list(self, p):
        return [p.function]

    # Runs when ')' of the header is matched, i.e. BEFORE the body is parsed.
    @_('return_type ID "(" param_list_opt ")"')
    def function_header(self, p):
        param_types = [q.type for q in p.param_list_opt]
        self.symbol_table.insert_function(p.ID, p.return_type, param_types)
        self.symbol_table.push_scope()
        self.local_counter = 0
        self.layout_entries = []
        for i, q in enumerate(p.param_list_opt):
            self.symbol_table.insert(q.name, q.type)
            self.layout_entries.append({
                "name": q.name,
                "kind": "parameter",
                "type": q.type,
                "offset": 8 + 4 * i,
                "size_bytes": 4,
            })
        self.current_return_type = p.return_type
        return (p.ID, p.return_type, p.param_list_opt)
    
    @_('function_header "{" statement_list "}"')
    def function(self, p):
        name, return_type, params = p.function_header
        layout = {
            "local_size": self.local_counter,
            "entries": self.layout_entries,
        }
        self.memory_layouts[name] = layout
        func = self.symbol_table.lookup_function(name)
        func.local_size = self.local_counter
        func.memory_layout = self.layout_entries
        self.symbol_table.pop_scope()
        self.current_return_type = None
        return FunctionDefinition(name, return_type, params, Block(p.statement_list))

    @_('INT')
    def return_type(self, p):
        return "int"

    @_('BOOL')
    def return_type(self, p):
        return "bool"

    @_('VOID')
    def return_type(self, p):
        return "void"

    # ---------------- parameters ----------------
    @_('param_list')
    def param_list_opt(self, p):
        return p.param_list

    @_('')
    def param_list_opt(self, p):
        return []

    @_('param_list "," param')
    def param_list(self, p):
        return p.param_list + [p.param]

    @_('param')
    def param_list(self, p):
        return [p.param]

    @_('INT ID')
    def param(self, p):
        return Parameter(p.ID, "int")

    @_('BOOL ID')
    def param(self, p):
        return Parameter(p.ID, "bool")

    # ---------------- statements ----------------
    @_('statement_list statement')
    def statement_list(self, p):
        return p.statement_list + [p.statement]

    @_('statement')
    def statement_list(self, p):
        return [p.statement]

    @_('INT ID ";"')
    def statement(self, p):
        self.symbol_table.insert(p.ID, "int")
        self.allocate(p.ID, "int", "variable")
        return VarDeclaration(p.ID, "int")

    @_('BOOL ID ";"')
    def statement(self, p):
        self.symbol_table.insert(p.ID, "bool")
        self.allocate(p.ID, "bool", "variable")
        return VarDeclaration(p.ID, "bool")

    @_('INT ID "[" NUMBER "]" ";"')
    def statement(self, p):
        if p.NUMBER <= 0:
            raise SemanticError("Array size must be a positive integer")
        self.symbol_table.insert(p.ID, "int", "array", p.NUMBER)
        self.allocate(p.ID, "int", "array", p.NUMBER)    
        return ArrayDeclaration(p.ID, "int", p.NUMBER)

    @_('BOOL ID "[" NUMBER "]" ";"')
    def statement(self, p):
        if p.NUMBER <= 0:
            raise SemanticError("Array size must be a positive integer")
        self.symbol_table.insert(p.ID, "bool", "array", p.NUMBER)
        self.allocate(p.ID, "bool", "array", p.NUMBER)
        return ArrayDeclaration(p.ID, "bool", p.NUMBER)

    @_('ID "[" expr "]" "=" expr ";"')
    def statement(self, p):
        sym = self.get_array(p.ID)
        self.check_index(p.expr0)
        if p.expr1.type != sym.type:
            raise SemanticError(
                f"Cannot assign {p.expr1.type} to element of {sym.type} array '{p.ID}'"
            )
        return ArrayAssignment(p.ID, p.expr0, p.expr1)

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

    # call used as a statement: must be void
    @_('ID "(" arg_list_opt ")" ";"')
    def statement(self, p):
        func = self.check_call(p.ID, p.arg_list_opt)
        if func.return_type != 'void':
            raise SemanticError(
                f"The result of non-void function '{p.ID}' cannot be "
                f"discarded; a call statement must be a void function"
            )
        return FunctionCall(p.ID, p.arg_list_opt, 'void')

    @_('ID "[" expr "]"')
    def primary(self, p):
        sym = self.get_array(p.ID)
        self.check_index(p.expr)
        return ArrayAccess(p.ID, p.expr, sym.type)

    @_('RETURN expr ";"')
    def statement(self, p):
        if self.current_return_type == 'void':
            raise SemanticError("'return' is not allowed in a void function")
        if p.expr.type != self.current_return_type:
            raise SemanticError(
                f"Return type mismatch: function returns "
                f"{self.current_return_type}, got {p.expr.type}"
            )
        return Return(p.expr)

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

    # ---------------- blocks (own scope) ----------------
    @_('"{"')
    def block_start(self, p):
        self.symbol_table.push_scope()

    @_('block_start statement_list "}"')
    def block(self, p):
        self.symbol_table.pop_scope()
        return Block(p.statement_list)

    # ---------------- call arguments ----------------
    @_('arg_list')
    def arg_list_opt(self, p):
        return p.arg_list

    @_('')
    def arg_list_opt(self, p):
        return []

    @_('arg_list "," expr')
    def arg_list(self, p):
        return p.arg_list + [p.expr]

    @_('expr')
    def arg_list(self, p):
        return [p.expr]

    # ---------------- expressions (lowest -> highest precedence) ----------------
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

    # call used inside an expression: must be non-void
    @_('ID "(" arg_list_opt ")"')
    def primary(self, p):
        func = self.check_call(p.ID, p.arg_list_opt)
        if func.return_type == 'void':
            raise SemanticError(
                f"The void function '{p.ID}' cannot be used in an expression"
            )
        return FunctionCall(p.ID, p.arg_list_opt, func.return_type)

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