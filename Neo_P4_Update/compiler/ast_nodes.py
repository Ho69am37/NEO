from dataclasses import dataclass
from typing import List, Optional


# -----------------------------------------------------
# AST nodes for Neo P4
#
# Expression nodes include a semantic type attribute.
# This attribute must be assigned during syntax-directed
# semantic analysis.
# -----------------------------------------------------


@dataclass
class Program:
    """Represents a complete Neo program."""

    statements: List[object]


@dataclass
class VarDeclaration:
    """Represents a variable declaration."""

    name: str
    var_type: str


@dataclass
class Assignment:
    """Represents an assignment statement."""

    name: str
    expression: object


@dataclass
class Move:
    """Represents a move statement."""

    expression: object


@dataclass
class Turn:
    """Represents a turn statement."""

    direction: str


# -----------------------------------------------------
# Expression nodes
# -----------------------------------------------------


@dataclass
class Number:
    """
    Represents an integer literal.

    The type attribute stores the semantic type assigned
    to this expression during syntax-directed analysis.
    """

    value: int
    type: Optional[str] = None


@dataclass
class Boolean:
    """
    Represents a Boolean literal.

    The type attribute stores the semantic type assigned
    to this expression during syntax-directed analysis.
    """

    value: bool
    type: Optional[str] = None


@dataclass
class Variable:
    """
    Represents the use of a variable in an expression.

    The type attribute stores the semantic type assigned
    to this expression during syntax-directed analysis.
    """

    name: str
    type: Optional[str] = None


@dataclass
class BinaryOp:
    """
    Represents a binary operation.

    The type attribute stores the semantic type assigned
    to this expression during syntax-directed analysis.
    """

    operator: str
    left: object
    right: object
    type: Optional[str] = None


@dataclass
class UnaryOp:
    """
    Represents a unary operation.

    The type attribute stores the semantic type assigned
    to this expression during syntax-directed analysis.
    """

    operator: str
    operand: object
    type: Optional[str] = None


@dataclass
class Sensor:
    """
    Represents a Neo sensor expression.

    The type attribute stores the semantic type assigned
    to this expression during syntax-directed analysis.
    """

    name: str
    type: Optional[str] = None