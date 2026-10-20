from compiler.ast_nodes import (
    VarDeclaration,
    Assignment,
    Number,
    Variable,
    BinaryOp,
    UnaryOp
)


class NeoEvaluator:
    """
    Runtime evaluator for Neo P2 expressions and variables.
    """

    def __init__(self):
        self.variables = {}

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
            # Variables are initialized to zero in Neo P2.
            self.variables[statement.name] = 0
            return

        # Assignment
        if isinstance(statement, Assignment):

            # A variable must be declared before assignment.
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
        Evaluate an expression and return its integer value.
        """

        # Integer literal
        if isinstance(expression, Number):
            return expression.value

        # Variable
        if isinstance(expression, Variable):

            if expression.name not in self.variables:
                raise RuntimeError(
                    f"undefined variable '{expression.name}'"
                )

            return self.variables[expression.name]

        # Unary operation
        if isinstance(expression, UnaryOp):

            value = self.evaluate(expression.operand)

            if expression.operator == "-":
                return -value

            raise RuntimeError(
                f"unknown unary operator '{expression.operator}'"
            )

        # Binary operation
        if isinstance(expression, BinaryOp):

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
                    raise RuntimeError(
                        "division by zero"
                    )

                # Integer division with truncation toward zero,
                # following the semantics used by C.
                quotient = abs(left) // abs(right)

                if (left < 0) != (right < 0):
                    quotient = -quotient

                return quotient

            raise RuntimeError(
                f"unknown binary operator '{expression.operator}'"
            )

        raise RuntimeError(
            f"cannot evaluate expression {expression!r}"
        )