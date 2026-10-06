from dataclasses import dataclass
from typing import List


# -----------------------------------------------------
# AST nodes provided for Neo P1
# -----------------------------------------------------
#
# DO NOT MODIFY THIS FILE.
#
# The parser must construct an AST using these node types.
# -----------------------------------------------------


@dataclass
class Move:
    """Represents a move(n) statement."""
    value: int


@dataclass
class Turn:
    """Represents a turn(LEFT) or turn(RIGHT) statement."""
    direction: str


@dataclass
class Program:
    """Represents a complete Neo program."""
    statements: List[object]