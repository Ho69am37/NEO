from dataclasses import dataclass
from typing import List


# -----------------------------------------------------
# AST nodes for Neo P2
# -----------------------------------------------------


@dataclass
class Program:
    """Represents a complete Neo program."""
    statements: List[object]


# -----------------------------------------------------
# Statements
# -----------------------------------------------------


@dataclass
class VarDeclaration:
    """Represents an integer variable declaration."""
    name: str


@dataclass
class Assignment:
    """Represents an assignment statement."""
    name: str
    expression: object


@dataclass
class Move:
    """Represents a move(expression) statement."""
    expression: object


@dataclass
class Turn:
    """Represents a turn(LEFT) or turn(RIGHT) statement."""
    direction: str


# -----------------------------------------------------
# Expressions
# -----------------------------------------------------


@dataclass
class Number:
    """Represents an integer constant."""
    value: int


@dataclass
class Variable:
    """Represents the use of a variable in an expression."""
    name: str


@dataclass
class BinaryOp:
    """Represents a binary arithmetic operation."""
    operator: str
    left: object
    right: object


@dataclass
class UnaryOp:
    """Represents a unary arithmetic operation."""
    operator: str
    operand: object