from compiler.lexer import NeoLexer
from compiler.parser import NeoParser
from compiler.symbol_table import SemanticError
from compiler.ast_nodes import Program, Block, If, While, Assignment, Move, Turn

results = []


def parse(src):
    return NeoParser().parse(NeoLexer().tokenize(src))


def check(label, ok, detail=""):
    results.append(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))


def expect_valid(label, src, verify=None):
    """Program must parse; optionally verify the shape of the AST."""
    try:
        prog = parse(src)
        if verify is not None:
            ok, detail = verify(prog)
            check(label, ok, detail)
        else:
            check(label, True)
    except Exception as ex:
        check(label, False, f"{type(ex).__name__}: {ex}")


def expect_error(label, src, exc_type):
    """Program must raise exactly the given kind of error."""
    try:
        parse(src)
        check(label, False, "was accepted")
    except exc_type as ex:
        check(label, True, f"-> {ex}")
    except Exception as ex:
        check(label, False, f"wrong exception {type(ex).__name__}: {ex}")


# ---------------------------------------------------------------
print("=== 1. if without else ===")
expect_valid(
    "if (obstacle()) { turn(LEFT); }",
    "if (obstacle()) { turn(LEFT); }",
    lambda p: (
        isinstance(p.statements[0], If)
        and p.statements[0].else_branch is None
        and isinstance(p.statements[0].then_branch, Block)
        and isinstance(p.statements[0].then_branch.statements[0], Turn),
        "else_branch must be None",
    ),
)

# ---------------------------------------------------------------
print("\n=== 2. if / else ===")
expect_valid(
    "if (goal()) { move(1); } else { turn(RIGHT); }",
    "if (goal()) { move(1); } else { turn(RIGHT); }",
    lambda p: (
        isinstance(p.statements[0], If)
        and isinstance(p.statements[0].then_branch, Block)
        and isinstance(p.statements[0].else_branch, Block)
        and isinstance(p.statements[0].then_branch.statements[0], Move)
        and isinstance(p.statements[0].else_branch.statements[0], Turn),
        "then and else branches must be Blocks",
    ),
)

# ---------------------------------------------------------------
print("\n=== 3. while loop ===")
expect_valid(
    "int s; s = 3; while (s > 0) { s = s - 1; }",
    "int s; s = 3; while (s > 0) { s = s - 1; }",
    lambda p: (
        isinstance(p.statements[2], While)
        and isinstance(p.statements[2].body, Block)
        and isinstance(p.statements[2].body.statements[0], Assignment)
        and p.statements[2].condition.type == "bool",
        "body must be a Block, condition typed bool",
    ),
)

# ---------------------------------------------------------------
print("\n=== 4. nested control flow ===")
expect_valid(
    "while inside if inside while",
    """
    int n;
    n = 2;
    while (n > 0) {
        if (obstacle()) {
            while (goal()) { move(1); }
        } else {
            if (n == 1) { turn(LEFT); }
        }
        n = n - 1;
    }
    """,
    lambda p: (
        isinstance(p.statements[2], While)
        and isinstance(p.statements[2].body.statements[0], If)
        and isinstance(p.statements[2].body.statements[0].then_branch.statements[0], While)
        and isinstance(p.statements[2].body.statements[0].else_branch.statements[0], If),
        "nesting not preserved in the AST",
    ),
)

# ---------------------------------------------------------------
print("\n=== 5. conditions with obstacle() and goal() ===")
expect_valid("if (obstacle())", "if (obstacle()) { move(1); }")
expect_valid("while (goal())", "while (goal()) { move(1); }")
expect_valid("!goal()", "while (!goal()) { move(1); }")
expect_valid("obstacle() && !goal()", "if (obstacle() && !goal()) { turn(LEFT); }")
expect_valid("obstacle() || goal()", "if (obstacle() || goal()) { turn(RIGHT); }")

# ---------------------------------------------------------------
print("\n=== 6. non-boolean if condition (SemanticError) ===")
expect_error("if (1)", "if (1) { move(1); }", SemanticError)
expect_error("if (int variable)", "int x; x = 1; if (x) { move(1); }", SemanticError)
expect_error("if (x + 1)", "int x; x = 1; if (x + 1) { move(1); }", SemanticError)

# ---------------------------------------------------------------
print("\n=== 7. non-boolean while condition (SemanticError) ===")
expect_error(
    "while (steps)  [example from the PDF]",
    "int steps; steps = 3; while (steps) { move(1); }",
    SemanticError,
)
expect_error("while (5)", "while (5) { move(1); }", SemanticError)

# ---------------------------------------------------------------
print("\n=== 8. empty block (SyntaxError) ===")
expect_error("if (true) { }", "if (true) { }", SyntaxError)
expect_error("while (true) { }", "while (true) { }", SyntaxError)
expect_error("else block empty", "if (true) { move(1); } else { }", SyntaxError)
expect_error("nested empty block", "while (true) { if (true) { } }", SyntaxError)

# ---------------------------------------------------------------
print("\n=== 9. declaration inside a block (SyntaxError) ===")
expect_error("int inside if", "if (true) { int x; }", SyntaxError)
expect_error("bool inside while", "while (true) { bool b; }", SyntaxError)
expect_error("declaration after a statement", "if (true) { move(1); int x; }", SyntaxError)
expect_error("declaration inside else", "if (true) { move(1); } else { bool b; }", SyntaxError)

# ---------------------------------------------------------------
print("\n=== Extra: braces are mandatory ===")
expect_error("if without braces", "if (true) move(1);", SyntaxError)
expect_error("while without braces", "while (true) move(1);", SyntaxError)

# ---------------------------------------------------------------
print("\n=== Extra: example program from the PDF ===")
expect_valid(
    "steps / blocked program",
    """
    int steps;
    bool blocked;

    steps = 2;

    while (steps > 0) {
        blocked = obstacle();

        if (blocked) {
            turn(LEFT);
        } else {
            move(1);
        }
        steps = steps - 1;
    }
    """,
    lambda p: (
        isinstance(p, Program) and len(p.statements) == 4,
        "expected 4 top-level statements",
    ),
)

# ---------------------------------------------------------------
print("\n=== Extra: Practice 3 / 4 checks still work ===")
expect_error("undeclared variable in block", "if (true) { z = 1; }", SemanticError)
expect_error("type mismatch in block", "int x; if (true) { x = true; }", SemanticError)
expect_error("move(bool) in block", "while (true) { move(true); }", SemanticError)
expect_valid("Practice 4 expression", "bool b; b = 1 + 2 < 3 * 4 == true && !goal() || obstacle();")

print(f"\n{sum(results)} passed, {len(results) - sum(results)} failed")