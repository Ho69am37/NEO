from compiler.ast_nodes import (
    Program, FunctionDefinition, Block, VarDeclaration, ArrayDeclaration,
    Assignment, ArrayAssignment, Move, Turn, If, While, Return, FunctionCall,
    Number, Boolean, Variable, ArrayAccess, BinaryOp, UnaryOp, Sensor
)


class CodeGenerationError(Exception):
    pass


class CodeGenerator:
    """
    Neo Practice 8 backend.

    Generate pedagogical 32-bit x86 assembly (AT&T syntax) directly
    from the AST produced by your parser.

    IMPORTANT:
    - Do not generate three-address code.
    - Expression results must be left in %eax.
    - Use the memory layout computed in Practice 7.
    """

    def __init__(self, memory_layouts):
        self.memory_layouts = memory_layouts
        self.lines = []
        self.current_function = None
        self.layout_entries = []
        self.layout_cursor = 0
        self.scopes = []
        self.label_counter = 0

    def generate(self, program):
        if not isinstance(program, Program):
            raise CodeGenerationError("expected a Program AST node")

        self.lines = [".text", ""]
        self.label_counter = 0

        for function in program.functions:
            self._generate_function(function)

        return "\n".join(self.lines).rstrip() + "\n"

    def _emit(self, line=""):
        self.lines.append(line)

    def _new_label(self, prefix):
        label = f".L_{prefix}_{self.label_counter}"
        self.label_counter += 1
        return label

    def _generate_function(self, function):
        """
        Infrastructure supplied for P8.

        The prologue uses the local_size computed in Practice 7.
        Parameters and local declarations are associated with their
        memory-layout entries while the AST is traversed.
        """
        if not isinstance(function, FunctionDefinition):
            raise CodeGenerationError(
                f"unsupported top-level node {type(function).__name__}"
            )

        if function.name not in self.memory_layouts:
            raise CodeGenerationError(
                f"missing memory layout for function '{function.name}'"
            )

        layout = self.memory_layouts[function.name]
        self.current_function = function.name
        self.layout_entries = layout["entries"]
        self.layout_cursor = 0
        self.scopes = [{}]

        for parameter in function.parameters:
            entry = self._next_layout_entry(parameter.name, "parameter")
            self.scopes[-1][parameter.name] = entry

        self._emit(f".globl {function.name}")
        self._emit(f"{function.name}:")
        self._emit("    pushl %ebp")
        self._emit("    movl %esp, %ebp")

        local_size = layout["local_size"]
        if local_size:
            self._emit(f"    subl ${local_size}, %esp")

        self._generate_block(function.body, create_scope=False)

        # A void function may fall through the end of its body.
        # A non-void function returns through its Return statement.
        if function.return_type == "void":
            self._emit("    leave")
            self._emit("    ret")

        self._emit("")
        self.current_function = None
        self.scopes = []

    def _generate_block(self, block, create_scope=True):
        if not isinstance(block, Block):
            raise CodeGenerationError("expected a Block AST node")

        if create_scope:
            self.scopes.append({})

        for statement in block.statements:
            self._generate_statement(statement)

        if create_scope:
            self.scopes.pop()

    def _generate_statement(self, statement):
        """
        TODO — PRACTICE 8

        Generate assembly for:
          - VarDeclaration / ArrayDeclaration
          - Assignment / ArrayAssignment
          - Move / Turn
          - If / While
          - Return
          - FunctionCall used as a statement

        Declarations do not emit assembly instructions, but they MUST
        register the corresponding memory-layout entry in the current
        lexical scope.

        Use _new_label() for control-flow labels.
        """
        #---declaration---
        if isinstance(statement, VarDeclaration):
            entry = self._next_layout_entry(statement.name, "variable")
            self.scopes[-1][statement.name] = entry
            return

        if isinstance(statement, ArrayDeclaration):
            entry = self._next_layout_entry(statement.name, "array")
            self.scopes[-1][statement.name] = entry
            return    

        #---assignments
        if isinstance(statement, Assignment):
            entry = self._lookup(statement.name)
            self._generate_expression(statement.expression)
            self._emit(f"    movl %eax, {entry['offset']}(%ebp)")
            return

        if isinstance(statement, ArrayAssignment):
            entry = self._lookup(statement.name)
            self._generate_expression(statement.index)
            self._emit("    pushl %eax")
            # save index
            self._generate_expression(statement.expression)
            self._emit("    popl %ecx")                   # index -> %ecx
            self._emit(f"    movl %eax, {entry['offset']}(%ebp,%ecx,4)")
            return

        #---Move/Turn---
        if isinstance(statement, Move):
            self._generate_expression(statement.expression)
            self._emit("    call neo_move")
            return

        if isinstance(statement, Turn):
            value = 0 if statement.direction == 'LEFT' else 1
            self._emit(f"    movl ${value}, %eax")
            self._emit("    call neo_turn")
            return

        # --- control flow ---
        if isinstance(statement, If):
            self._generate_expression(statement.condition)
            self._emit("    cmpl $0, %eax")
            if statement.else_branch is None:
                end_label = self._new_label("if_final")
                self._emit(f"    je {end_label}")
                self._generate_block(statement.then_branch)
                self._emit(f"{end_label}:")
            else:
                else_label = self._new_label("else")
                end_label = self._new_label("if_final")
                self._emit(f"    je {else_label}")
                self._generate_block(statement.then_branch)
                self._emit(f"    jmp {end_label}")
                self._emit(f"{else_label}:")
                self._generate_block(statement.else_branch)
                self._emit(f"{end_label}:")
            return

        if isinstance(statement, While):
            start_label = self._new_label("while_start")
            end_label = self._new_label("while_final")
            self._emit(f"{start_label}:")
            self._generate_expression(statement.condition)
            self._emit("    cmpl $0, %eax")
            self._emit(f"    je {end_label}")
            self._generate_block(statement.body)
            self._emit(f"    jmp {start_label}")
            self._emit(f"{end_label}:")
            return

        # --- functions ---
        if isinstance(statement, Return):
            self._generate_expression(statement.expression)
            self._emit("    leave")
            self._emit("    ret")
            return

        if isinstance(statement, FunctionCall):
            self._generate_call(statement)
            return

        raise CodeGenerationError(
            f"unsupported statement {type(statement).__name__}"
        )

    

    
# ------------------------------------------------------------------
    # Expressions
    # ------------------------------------------------------------------
    _COMPARISONS = {
        "<": "setl",
        "<=": "setle",
        ">": "setg",
        ">=": "setge",
        "==": "sete",
        "!=": "setne",
    }     

    def _generate_expression(self, expression):
        """
        TODO — PRACTICE 8

        Generate assembly for:
          - Number / Boolean
          - Variable / ArrayAccess
          - BinaryOp: + - * / < <= > >= == != && ||
          - UnaryOp: - !
          - FunctionCall
          - Sensor: obstacle() / goal()

        Convention:
            the value of every expression is returned in %eax.

        Boolean values:
            false = 0
            true  = 1

        Preserve short-circuit evaluation for && and ||.

        Signed integer division must use:
            cdq
            idivl <divisor>
        """
        if isinstance(expression, Number):
            self._emit(f"    movl ${expression.value}, %eax")
            return

        if isinstance(expression, Boolean):
            self._emit(f"    movl ${1 if expression.value else 0}, %eax")
            return

        if isinstance(expression, Variable):
            entry = self._lookup(expression.name)
            self._emit(f"    movl {entry['offset']}(%ebp), %eax")
            return

        if isinstance(expression, ArrayAccess):
            entry = self._lookup(expression.name)
            self._generate_expression(expression.index)
            self._emit("    movl %eax, %ecx")
            self._emit(f"    movl {entry['offset']}(%ebp,%ecx,4), %eax")
            return

        if isinstance(expression, Sensor):
            if expression.name == "obstacle":
                self._emit("    call neo_obstacle")
            elif expression.name == "goal":
                self._emit("    call neo_goal")
            else:
                raise CodeGenerationError(
                    f"unknown sensor '{expression.name}'"
                )
            return

        if isinstance(expression, FunctionCall):
            self._generate_call(expression)
            return

        if isinstance(expression, UnaryOp):
            self._generate_expression(expression.operand)
            if expression.operator == "-":
                self._emit("    negl %eax")
            elif expression.operator == "!":
                self._emit("    cmpl $0, %eax")
                self._emit("    sete %al")
                self._emit("    movzbl %al, %eax")
            else:
                raise CodeGenerationError(
                    f"unknown unary operator '{expression.operator}'"
                )
            return

        if isinstance(expression, BinaryOp):
            op = expression.operator

            # Short-circuit operators.
            if op == "&&":
                final = self._new_label("and_final")
                self._generate_expression(expression.left)
                self._emit("    cmpl $0, %eax")
                self._emit(f"    je {final}")
                self._generate_expression(expression.right)
                self._emit(f"{final}:")
                return

            if op == "||":
                final = self._new_label("or_final")
                self._generate_expression(expression.left)
                self._emit("    cmpl $0, %eax")
                self._emit(f"    jne {final}")
                self._generate_expression(expression.right)
                self._emit(f"{final}:")
                return

            # Strict operators: left -> stack, right -> %ebx, left -> %eax.
            self._generate_expression(expression.left)
            self._emit("    pushl %eax")
            self._generate_expression(expression.right)
            self._emit("    movl %eax, %ebx")
            self._emit("    popl %eax")

            if op == "+":
                self._emit("    addl %ebx, %eax")
            elif op == "-":
                self._emit("    subl %ebx, %eax")
            elif op == "*":
                self._emit("    imull %ebx, %eax")
            elif op == "/":
                self._emit("    cdq")
                self._emit("    idivl %ebx")
            elif op in self._COMPARISONS:
                self._emit("    cmpl %ebx, %eax")
                self._emit(f"    {self._COMPARISONS[op]} %al")
                self._emit("    movzbl %al, %eax")
            else:
                raise CodeGenerationError(
                    f"unknown binary operator '{op}'"
                )
            return

        raise CodeGenerationError(
            f"unsupported expression {type(expression).__name__}"
        )

    def _generate_call(self, call):
        """
        TODO — PRACTICE 8

        Use a cdecl-style convention:
          - push arguments right-to-left;
          - call the function;
          - caller removes arguments from the stack;
          - a non-void result remains in %eax.

        Therefore, in the callee:
            first parameter  -> 8(%ebp)
            second parameter -> 12(%ebp)
            ...
        """
        #push arguments right-to-left;
        for argument in reversed(call.arguments):
            self._generate_expression(argument)
            self._emit("    pushl %eax")

        self._emit(f"    call {call.name}")
        # Caller removes the arguments.
        if call.arguments:
            self._emit(f"    addl ${4 * len(call.arguments)}, %esp")    

    def _lookup(self, name):
        """Resolve a visible identifier in the reconstructed lexical scopes."""
        for scope in reversed(self.scopes):
            if name in scope:
                return scope[name]
        raise CodeGenerationError(
            f"no storage location found for '{name}'"
        )

    def _next_layout_entry(self, name, kind):
        """
        Associate the next declaration encountered in the AST with the
        corresponding Practice-7 memory-layout entry.
        """
        if self.layout_cursor >= len(self.layout_entries):
            raise CodeGenerationError(
                f"memory layout exhausted while resolving '{name}'"
            )

        entry = self.layout_entries[self.layout_cursor]
        self.layout_cursor += 1

        if entry["name"] != name or entry["kind"] != kind:
            raise CodeGenerationError(
                "AST and memory layout are inconsistent: "
                f"expected {kind} '{name}', found "
                f"{entry['kind']} '{entry['name']}'"
            )

        return entry
