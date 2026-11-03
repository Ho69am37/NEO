from compiler.ast_nodes import (
    VarDeclaration,
    Assignment,
    Number,
    Boolean,
    Variable,
    BinaryOp,
    UnaryOp,
    Sensor
)


class NeoEvaluator:
    """
    Runtime evaluator for Neo P4 expressions and variables.
    """

    def __init__(self, obstacle_sensor=None, goal_sensor=None):
        self.variables = {}
        self.obstacle_sensor = obstacle_sensor
        self.goal_sensor = goal_sensor

    def reset(self):
        """Reset the runtime environment."""
        self.variables = {}

    # -----------------------------------------------------
    # Statements
    # -----------------------------------------------------

    def execute_statement(self, statement):
        """
        Execute a statement that affects the runtime
        variable environment.
        """

        # Variable declaration
        if isinstance(statement, VarDeclaration):

            if statement.var_type == "int":
                self.variables[statement.name] = 0

            elif statement.var_type == "bool":
                self.variables[statement.name] = False

            else:
                raise RuntimeError(
                    f"unknown variable type '{statement.var_type}'"
                )

            return

        # Assignment
        if isinstance(statement, Assignment):

            # This check is kept defensively at runtime.
            # Correct P4 programs have already been checked
            # during semantic analysis.
            if statement.name not in self.variables:
                raise RuntimeError(
                    f"undefined variable '{statement.name}'"
                )

            value = self.evaluate(statement.expression)
            self.variables[statement.name] = value
            return

        raise RuntimeError(
            f"unsupported statement {statement!r}"
        )

    # -----------------------------------------------------
    # Expressions
    # -----------------------------------------------------

    def evaluate(self, expression):
        """
        Evaluate a Neo expression and return its value.
        """

        # Integer literal
        if isinstance(expression, Number):
            return expression.value

        # Boolean literal
        if isinstance(expression, Boolean):
            return expression.value

        # Variable
        if isinstance(expression, Variable):

            if expression.name not in self.variables:
                raise RuntimeError(
                    f"undefined variable '{expression.name}'"
                )

            return self.variables[expression.name]

        # Sensor
        if isinstance(expression, Sensor):

            if expression.name == "obstacle":

                if self.obstacle_sensor is None:
                    raise RuntimeError(
                        "obstacle sensor is not available"
                    )

                return self.obstacle_sensor()

            if expression.name == "goal":

                if self.goal_sensor is None:
                    raise RuntimeError(
                        "goal sensor is not available"
                    )

                return self.goal_sensor()

            raise RuntimeError(
                f"unknown sensor '{expression.name}'"
            )

        # Unary operation
        if isinstance(expression, UnaryOp):

            value = self.evaluate(expression.operand)

            if expression.operator == "-":
                return -value

            if expression.operator == "!":
                return not value

            raise RuntimeError(
                f"unknown unary operator '{expression.operator}'"
            )

        # Binary operation
        if isinstance(expression, BinaryOp):

            left = self.evaluate(expression.left)
            right = self.evaluate(expression.right)

            # Arithmetic operators
            if expression.operator == "+":
                return left + right

            if expression.operator == "-":
                return left - right

            if expression.operator == "*":
                return left * right

            if expression.operator == "/":

                if right == 0:
                    raise RuntimeError(
                        "division by zero"
                    )

                # Integer division with truncation toward zero,
                # following the semantics used by C.
                quotient = abs(left) // abs(right)

                if (left < 0) != (right < 0):
                    quotient = -quotient

                return quotient

            # Relational operators
            if expression.operator == "<":
                return left < right

            if expression.operator == "<=":
                return left <= right

            if expression.operator == ">":
                return left > right

            if expression.operator == ">=":
                return left >= right

            # Equality operators
            if expression.operator == "==":
                return left == right

            if expression.operator == "!=":
                return left != right

            # Logical operators
            if expression.operator == "&&":
                return left and right

            if expression.operator == "||":
                return left or right

            raise RuntimeError(
                f"unknown binary operator '{expression.operator}'"
            )

        raise RuntimeError(
            f"cannot evaluate expression {expression!r}"
        )