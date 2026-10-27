from compiler.lexer import NeoLexer
from compiler.parser import NeoParser

DECLS = "int x; int y; bool b; bool c; "


def show(n):
    """Turn an AST node into a fully parenthesized string."""
    name = type(n).__name__
    vals = list(vars(n).values()) if hasattr(n, "__dict__") else []
    if name == "BinaryOp":              # first 3 fields: op, left, right
        op, l, r = vals[:3]
        return f"({show(l)} {op} {show(r)})"
    if name == "UnaryOp":               # first 2 fields: op, operand
        op, o = vals[:2]
        return f"({op}{show(o)})"
    if name == "Number":
        return str(vals[0])
    if name == "Boolean":
        return "true" if vals[0] else "false"
    if name == "Variable":
        return str(vals[0])
    if name == "Sensor":
        return f"{vals[0]}()"
    return repr(n)

def parse_expr(expr):
    """Parse 'x = <expr>;' after some declarations and return the expr AST."""
    code = DECLS + f"x = {expr};"
    program = NeoParser().parse(NeoLexer().tokenize(code))
    stmts = next(v for v in vars(program).values() if isinstance(v, list))
    assignment = stmts[-1]
    return list(vars(assignment).values())[-1]   # Assignment(ID, expr)


PRECEDENCE_TESTS = [
    # (input, expected fully-parenthesized form)
    ("1 + 2 * 3",         "(1 + (2 * 3))"),
    ("1 - 2 - 3",         "((1 - 2) - 3)"),
    ("8 / 4 / 2",         "((8 / 4) / 2)"),
    ("(1 + 2) * 3",       "((1 + 2) * 3)"),
    ("-x * y",            "((-x) * y)"),
    ("!!true",            "(!(!true))"),
    ("1 + 2 < 3 * 4",     "((1 + 2) < (3 * 4))"),
    ("1 < 2 == true",     "((1 < 2) == true)"),
    ("x <= 10 || x != 3", "((x <= 10) || (x != 3))"),
    ("x >= y",            "(x >= y)"),
    ("b || c || true",    "((b || c) || true)"),
    ("b && c && true",    "((b && c) && true)"),
    ("true || false && true", "(true || (false && true))"),
    ("!goal() && obstacle()", "((!goal()) && obstacle())"),
    ("1 + 2 < 3 * 4 == true && !goal() || obstacle()",
     "(((((1 + 2) < (3 * 4)) == true) && (!goal())) || obstacle())"),
]

ERROR_TESTS = [
    "x = ;",              # missing expression
    "x = 1 +;",           # dangling operator
    "x = (1 + 2;",        # unbalanced paren
    "x = obstacle;",      # sensor without ()
    "x = 1 && ;",         # dangling &&
]


def main():
    passed = failed = 0

    print("=== Precedence / associativity ===")
    for src, expected in PRECEDENCE_TESTS:
        try:
            got = show(parse_expr(src))
        except Exception as e:
            got = f"EXCEPTION: {e}"
        ok = got == expected
        passed += ok
        failed += not ok
        print(f"[{'OK' if ok else 'FAIL'}] {src}")
        if not ok:
            print(f"       expected: {expected}")
            print(f"       got:      {got}")

    print("\n=== Should be rejected ===")
    for src in ERROR_TESTS:
        try:
            parse_expr(src.removeprefix("x = ").removesuffix(";"))
            ok = False
        except Exception as e:
            ok = True
            msg = str(e)
        passed += ok
        failed += not ok
        print(f"[{'OK' if ok else 'FAIL'}] {src}" + (f"   -> {msg}" if ok else "   (was accepted!)"))

    print("\n=== Undeclared variable ===")
    try:
        NeoParser().parse(NeoLexer().tokenize("z = 5;"))
        print("[FAIL] undeclared variable was accepted")
        failed += 1
    except Exception as e:
        print(f"[OK] rejected -> {e}")
        passed += 1

    print("\n=== Full program ===")
    program_src = """
    int x;
    bool done;
    x = 3;
    done = obstacle() || goal();
    move(x + 1);
    turn(LEFT);
    """
    try:
        prog = NeoParser().parse(NeoLexer().tokenize(program_src))
        print("[OK] parsed:", prog)
        passed += 1
    except Exception as e:
        print("[FAIL]", e)
        failed += 1

    print(f"\n{passed} passed, {failed} failed")


if __name__ == "__main__":
    main()