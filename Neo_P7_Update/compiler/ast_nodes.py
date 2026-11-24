from dataclasses import dataclass
from typing import List, Optional


# -----------------------------------------------------
# AST nodes for Neo P7
# -----------------------------------------------------


@dataclass
class Program:
    """Represents a complete Neo program."""
    functions: List[object]


# -----------------------------------------------------
# Statements
# -----------------------------------------------------


@dataclass
class VarDeclaration:
    """Represents a variable declaration."""
    name: str
    var_type: str


@dataclass
class ArrayDeclaration:
    """Represents a fixed-size one-dimensional array declaration."""
    name: str
    element_type: str
    size: int


@dataclass
class Assignment:
    """Represents an assignment statement."""
    name: str
    expression: object


@dataclass
class ArrayAssignment:
    """Represents an assignment to one array element."""
    name: str
    index: object
    expression: object


@dataclass
class Move:
    """Represents a move(expression) statement."""
    expression: object


@dataclass
class Turn:
    """Represents a turn(LEFT) or turn(RIGHT) statement."""
    direction: str


@dataclass
class Block:
    """
    Represents a non-empty block of Neo statements.
    """
    statements: List[object]


@dataclass
class If:
    """
    Represents an if or if-else statement.
    """
    condition: object
    then_branch: Block
    else_branch: Optional[Block] = None


@dataclass
class While:
    """
    Represents a while statement.
    """
    condition: object
    body: Block


# -----------------------------------------------------
# Functions
# -----------------------------------------------------


@dataclass
class Parameter:
    """Represents a function parameter."""
    name: str
    type: str


@dataclass
class FunctionDefinition:
    """Represents a function definition."""
    name: str
    return_type: str
    parameters: List[object]
    body: Block


@dataclass
class FunctionCall:
    """Represents a function call."""
    name: str
    arguments: List[object]
    type: Optional[str] = None


@dataclass
class Return:
    """Represents a return statement."""
    expression: object

# -----------------------------------------------------
# Expressions
# -----------------------------------------------------


@dataclass
class Number:
    """Represents an integer constant."""
    value: int
    type: Optional[str] = None


@dataclass
class Boolean:
    """Represents a boolean constant."""
    value: bool
    type: Optional[str] = None


@dataclass
class Variable:
    """Represents the use of a variable in an expression."""
    name: str
    type: Optional[str] = None


@dataclass
class ArrayAccess:
    """Represents the use of one array element in an expression."""
    name: str
    index: object
    type: Optional[str] = None


@dataclass
class BinaryOp:
    """Represents a binary operation."""
    operator: str
    left: object
    right: object
    type: Optional[str] = None


@dataclass
class UnaryOp:
    """Represents a unary operation."""
    operator: str
    operand: object
    type: Optional[str] = None


@dataclass
class Sensor:
    """Represents a Neo sensor call."""
    name: str
    type: Optional[str] = None