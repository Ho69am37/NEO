from compiler.lexer import NeoLexer
from compiler.parser import NeoParser
from compiler.symbol_table import SemanticError
from compiler.ast_nodes import (
    Assignment, Move, Number, Boolean, Variable, BinaryOp, UnaryOp, Sensor
)

DECLS = "int x; int y; bool b; bool c; "


def parse(src):
    return NeoParser().parse(NeoLexer().tokenize(src))


def show(n):
    name = type(n).__name__
    if name == "BinaryOp":
        return f"({show(n.left)} {n.operator} {show(n.right)})"
    if name == "UnaryOp":
        return f"({n.operator}{show(n.operand)})"
    if name == "Number":
        return str(n.value)
    if name == "Boolean":
        return "true" if n.value else "false"
    if name == "Variable":
        return n.name
    if name == "Sensor":
        return f"{n.name}()"
    return repr(n)


def all_typed(n):
    """True if every expression node under n has a non-None type."""
    if isinstance(n, (Number, Boolean, Variable, Sensor)):
        return n.type is not None
    if isinstance(n, BinaryOp):
        return n.type is not None and all_typed(n.left) and all_typed(n.right)
    if isinstance(n, UnaryOp):
        return n.type is not None and all_typed(n.operand)
    return True


results = []


def check(label, ok, detail=""):
    results.append(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))


# 1. Precedence / associativity + expression types
PREC = [
    ("1 + 2 * 3",          "(1 + (2 * 3))",        "int", "x"),
    ("1 - 2 - 3",          "((1 - 2) - 3)",        "int", "x"),
    ("-x * y",             "((-x) * y)",           "int", "x"),
    ("1 + 2 < 3 * 4",      "((1 + 2) < (3 * 4))",  "bool", "b"),
    ("1 < 2 == true",      "((1 < 2) == true)",    "bool", "b"),
    ("b || c || true",     "((b || c) || true)",   "bool", "b"),
    ("true || false && c", "(true || (false && c))", "bool", "b"),
    ("!goal() && obstacle()", "((!goal()) && obstacle())", "bool", "b"),
    ("x <= 10 || x != 3",  "((x <= 10) || (x != 3))", "bool", "b"),
    ("x + 1 >= y - 2 && !b", "(((x + 1) >= (y - 2)) && (!b))", "bool", "b"),
    ("b == c",             "(b == c)",             "bool", "b"),
    ("!!true",             "(!(!true))",           "bool", "b"),
]

print("=== Valid expressions: shape and type ===")
for expr, shape, typ, target in PREC:
    try:
        prog = parse(DECLS + f"{target} = {expr};")
        e = prog.statements[-1].expression
        check(expr, show(e) == shape and e.type == typ and all_typed(e),
              "" if show(e) == shape and e.type == typ
              else f"got {show(e)} : {e.type}")
    except Exception as ex:
        check(expr, False, f"EXCEPTION {type(ex).__name__}: {ex}")

# 2. Valid programs
VALID = [
    "int x; x = 1 + 2 * 3;",
    "bool b; b = 1 < 2;",
    "bool b; b = obstacle() || goal();",
    "bool b; b = true == false;",
    "int x; bool b; b = x <= 3 && !goal();",
    "move(2 + 3);",
    "int x; x = 3; move(x); turn(LEFT); turn(RIGHT);",
]
print("\n=== Valid programs ===")
for src in VALID:
    try:
        parse(src)
        check(src, True)
    except Exception as ex:
        check(src, False, f"{type(ex).__name__}: {ex}")

# 3. Semantic errors (must raise SemanticError)
SEM = [
    "int x; x = true;",
    "bool b; b = 5;",
    "int x; x = 1 < 2;",
    "int x; x = 1 && 2;",
    "bool b; b = 1 || true;",
    "bool b; b = !5;",
    "int x; x = -true;",
    "int x; bool b; b = x == b;",
    "bool b; b = true < false;",
    "bool b; int x; x = b + 1;",
    "move(true);",
    "bool b; move(b);",
    "move(obstacle());",
    "z = 5;",              # undeclared (Practice 3)
    "x = y + 1;",          # undeclared (Practice 3)
    "int x; int x;",       # redeclaration (Practice 3)
    "int x; bool x;",      # redeclaration, different type (Practice 3)
]
print("\n=== Semantic errors (expect SemanticError) ===")
for src in SEM:
    try:
        parse(src)
        check(src, False, "was accepted")
    except SemanticError as ex:
        check(src, True, f"-> {ex}")
    except Exception as ex:
        check(src, False, f"wrong exception {type(ex).__name__}: {ex}")

# 4. Syntax errors (must raise SyntaxError)
SYN = ["int x; x = ;", "int x; x = 1 +;", "int x; x = (1 + 2;",
       "bool b; b = obstacle;", "bool b; b = 1 && ;"]
print("\n=== Syntax errors (expect SyntaxError) ===")
for src in SYN:
    try:
        parse(src)
        check(src, False, "was accepted")
    except SyntaxError as ex:
        check(src, True, f"-> {ex}")
    except Exception as ex:
        check(src, False, f"wrong exception {type(ex).__name__}: {ex}")

print(f"\n{sum(results)} passed, {len(results) - sum(results)} failed")