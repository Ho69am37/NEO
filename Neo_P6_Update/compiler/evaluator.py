from compiler.ast_nodes import (
    VarDeclaration, Assignment, Move, Turn, Number, Boolean, Variable,
    BinaryOp, UnaryOp, Sensor, If, While, FunctionCall, Return
)


class ReturnSignal(Exception):
    """Internal signal used to return a value from a function."""
    def __init__(self, value):
        self.value = value


class NeoEvaluator:
    """Single runtime execution engine for Neo P6."""

    def __init__(self, obstacle_sensor=None, goal_sensor=None,
                 move_action=None, turn_action=None):
        self.frames = []
        self.functions = {}
        self.obstacle_sensor = obstacle_sensor
        self.goal_sensor = goal_sensor
        self.move_action = move_action
        self.turn_action = turn_action

    def reset(self):
        self.frames = []
        self.functions = {}

    def push_frame(self):
        self.frames.append([{}])

    def pop_frame(self):
        if not self.frames:
            raise RuntimeError("No activation record to remove")
        self.frames.pop()

    def push_scope(self):
        if not self.frames:
            raise RuntimeError("No active function")
        self.frames[-1].append({})

    def pop_scope(self):
        if not self.frames:
            raise RuntimeError("No active function")
        if len(self.frames[-1]) == 1:
            raise RuntimeError("Cannot remove the function scope")
        self.frames[-1].pop()

    def declare_variable(self, name, value=0):
        if not self.frames:
            raise RuntimeError("No active function")
        self.frames[-1][-1][name] = value

    def set_variable(self, name, value):
        if not self.frames:
            raise RuntimeError("No active function")
        for scope in reversed(self.frames[-1]):
            if name in scope:
                scope[name] = value
                return
        raise RuntimeError(f"undefined variable '{name}'")

    def get_variable(self, name):
        if not self.frames:
            raise RuntimeError("No active function")
        for scope in reversed(self.frames[-1]):
            if name in scope:
                return scope[name]
        raise RuntimeError(f"undefined variable '{name}'")

    def register_functions(self, program):
        self.functions = {f.name: f for f in program.functions}

    def execute_program(self, program):
        self.register_functions(program)
        return self.call_function("main", [])

    def call_function(self, name, arguments):
        if name not in self.functions:
            raise RuntimeError(f"undefined function '{name}'")

        function = self.functions[name]

        if len(arguments) != len(function.parameters):
            raise RuntimeError(
                f"function '{name}' received an invalid number of arguments"
            )

        # Arguments are evaluated in the caller activation record.
        argument_values = [self.evaluate(arg) for arg in arguments]

        self.push_frame()
        try:
            for parameter, value in zip(function.parameters, argument_values):
                self.declare_variable(parameter.name, value)

            try:
                for statement in function.body.statements:
                    self.execute_statement(statement)
            except ReturnSignal as signal:
                return signal.value

            if function.return_type != "void":
                raise RuntimeError(
                    f"function '{name}' finished without returning a value"
                )
            return None
        finally:
            self.pop_frame()

    def execute_block(self, block):
        self.push_scope()
        try:
            for statement in block.statements:
                self.execute_statement(statement)
        finally:
            self.pop_scope()

    def execute_statement(self, statement):
        if isinstance(statement, VarDeclaration):
            if statement.var_type == "int":
                self.declare_variable(statement.name, 0)
            elif statement.var_type == "bool":
                self.declare_variable(statement.name, False)
            else:
                raise RuntimeError(
                    f"unknown variable type '{statement.var_type}'"
                )
            return

        if isinstance(statement, Assignment):
            self.set_variable(
                statement.name,
                self.evaluate(statement.expression)
            )
            return

        if isinstance(statement, Move):
            steps = self.evaluate(statement.expression)
            if steps < 0:
                raise RuntimeError(
                    "move() expected a non-negative number of steps"
                )
            if self.move_action is None:
                raise RuntimeError("move action is not available")
            self.move_action(steps)
            return

        if isinstance(statement, Turn):
            if self.turn_action is None:
                raise RuntimeError("turn action is not available")
            self.turn_action(statement.direction)
            return

        if isinstance(statement, If):
            condition = self.evaluate(statement.condition)
            if condition:
                self.execute_block(statement.then_branch)
            elif statement.else_branch is not None:
                self.execute_block(statement.else_branch)
            return

        if isinstance(statement, While):
            while self.evaluate(statement.condition):
                self.execute_block(statement.body)
            return

        if isinstance(statement, FunctionCall):
            self.call_function(statement.name, statement.arguments)
            return

        if isinstance(statement, Return):
            raise ReturnSignal(
                self.evaluate(statement.expression)
            )

        raise RuntimeError(f"unsupported statement {statement!r}")

    def evaluate(self, expression):
        if isinstance(expression, Number):
            return expression.value

        if isinstance(expression, Boolean):
            return expression.value

        if isinstance(expression, Variable):
            return self.get_variable(expression.name)

        if isinstance(expression, Sensor):
            if expression.name == "obstacle":
                if self.obstacle_sensor is None:
                    raise RuntimeError("obstacle sensor is not available")
                return self.obstacle_sensor()

            if expression.name == "goal":
                if self.goal_sensor is None:
                    raise RuntimeError("goal sensor is not available")
                return self.goal_sensor()

            raise RuntimeError(f"unknown sensor '{expression.name}'")

        if isinstance(expression, UnaryOp):
            value = self.evaluate(expression.operand)
            if expression.operator == "-":
                return -value
            if expression.operator == "!":
                return not value
            raise RuntimeError(
                f"unknown unary operator '{expression.operator}'"
            )

        if isinstance(expression, BinaryOp):
            # C-like short-circuit evaluation.
            if expression.operator == "&&":
                left = self.evaluate(expression.left)
                if not left:
                    return False
                return self.evaluate(expression.right)

            if expression.operator == "||":
                left = self.evaluate(expression.left)
                if left:
                    return True
                return self.evaluate(expression.right)

            left = self.evaluate(expression.left)
            right = self.evaluate(expression.right)

            if expression.operator == "+":
                return left + right
            if expression.operator == "-":
                return left - right
            if expression.operator == "*":
                return left * right

            if expression.operator == "/":
                if right == 0:
                    raise RuntimeError("division by zero")
                quotient = abs(left) // abs(right)
                if (left < 0) != (right < 0):
                    quotient = -quotient
                return quotient

            if expression.operator == "<":
                return left < right
            if expression.operator == "<=":
                return left <= right
            if expression.operator == ">":
                return left > right
            if expression.operator == ">=":
                return left >= right
            if expression.operator == "==":
                return left == right
            if expression.operator == "!=":
                return left != right

            raise RuntimeError(
                f"unknown binary operator '{expression.operator}'"
            )

        if isinstance(expression, FunctionCall):
            return self.call_function(
                expression.name,
                expression.arguments
            )

        raise RuntimeError(
            f"cannot evaluate expression {expression!r}"
        )
