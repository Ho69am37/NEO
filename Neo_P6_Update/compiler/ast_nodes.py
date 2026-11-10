from dataclasses import dataclass
from typing import List, Optional


@dataclass
class Program:
    functions: List[object]


@dataclass
class Parameter:
    name: str
    type: str


@dataclass
class FunctionDefinition:
    name: str
    return_type: str
    parameters: List[Parameter]
    body: object


@dataclass
class VarDeclaration:
    name: str
    var_type: str


@dataclass
class Assignment:
    name: str
    expression: object


@dataclass
class Move:
    expression: object


@dataclass
class Turn:
    direction: str


@dataclass
class Block:
    statements: List[object]


@dataclass
class If:
    condition: object
    then_branch: Block
    else_branch: Optional[Block] = None


@dataclass
class While:
    condition: object
    body: Block


@dataclass
class FunctionCall:
    name: str
    arguments: List[object]
    type: Optional[str] = None


@dataclass
class Return:
    expression: object


@dataclass
class Number:
    value: int
    type: str = "int"


@dataclass
class Boolean:
    value: bool
    type: str = "bool"


@dataclass
class Variable:
    name: str
    type: Optional[str] = None


@dataclass
class BinaryOp:
    operator: str
    left: object
    right: object
    type: Optional[str] = None


@dataclass
class UnaryOp:
    operator: str
    operand: object
    type: Optional[str] = None


@dataclass
class Sensor:
    name: str
    type: str = "bool"
