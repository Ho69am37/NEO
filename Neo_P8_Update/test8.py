"""
Neo P8 test suite.

Place this file in the project root (next to neo.py and compiler/) and run:

    python test_neo.py            # run everything
    python test_neo.py -v         # also print generated assembly for each test
    python test_neo.py fact       # run only tests whose name contains "fact"

For every program it checks:
  1. the program compiles (lexer + parser + semantic actions)
  2. the generated assembly contains the expected instructions
  3. generic assembly sanity (4-space indent, '%' on registers,
     unique labels, every jump target defined, ret at the end)
  4. the evaluator produces the expected robot events
"""
import re
import sys

from compiler.lexer import NeoLexer
from compiler.parser import NeoParser
from compiler.symbol_table import SemanticError
from compiler.code_generator import CodeGenerator
from compiler.evaluator import NeoEvaluator


# ----------------------------------------------------------------------
# Helpers
# ----------------------------------------------------------------------
def compile_neo(src):
    parser = NeoParser()
    ast = parser.parse(NeoLexer().tokenize(src))
    asm = CodeGenerator(parser.memory_layouts).generate(ast)
    return ast, asm


def run_neo(ast, obstacles=None, goals=None):
    """Run the AST in the evaluator with a fake robot. Returns the events."""
    events = []
    obstacles = list(obstacles or [])
    goals = list(goals or [])

    def obstacle():
        return obstacles.pop(0) if obstacles else False

    def goal():
        return goals.pop(0) if goals else False

    ev = NeoEvaluator(
        obstacle_sensor=obstacle,
        goal_sensor=goal,
        move_action=lambda n: events.append(("move", n)),
        turn_action=lambda d: events.append(("turn", d)),
    )
    ev.execute_program(ast)
    return events


def check_asm_sanity(asm):
    problems = []
    lines = asm.splitlines()
    labels, jumps = [], []
    for i, line in enumerate(lines, 1):
        s = line.strip()
        if not s or s.startswith("#") or s in (".text",):
            continue
        if s.startswith(".globl"):
            continue
        if s.endswith(":"):
            labels.append(s[:-1])
            continue
        if not line.startswith("    ") or line.startswith("     "):
            problems.append(f"line {i}: bad indentation -> {line!r}")
        for reg in ("eax", "ebx", "ecx", "edx", "esp", "ebp"):
            if re.search(rf"(?<![%\w]){reg}\b", s):
                problems.append(f"line {i}: register without '%' -> {line!r}")
        m = re.match(r"(j\w+)\s+(\S+)", s)
        if m:
            jumps.append(m.group(2))
    dup = {l for l in labels if labels.count(l) > 1}
    if dup:
        problems.append(f"duplicate labels: {sorted(dup)}")
    for j in jumps:
        if j not in labels:
            problems.append(f"jump to undefined label {j}")
    if "ret" not in asm:
        problems.append("no 'ret' found")
    return problems


def in_order(asm, patterns):
    """True if the regex patterns appear in asm in the given order."""
    pos = 0
    for p in patterns:
        m = re.compile(p).search(asm, pos)
        if not m:
            return False, p
        pos = m.end()
    return True, None


# ----------------------------------------------------------------------
# Test cases
#   has      : substrings that must appear in the assembly
#   hasnt    : substrings that must NOT appear
#   order    : regexes that must appear in this order
#   events   : expected evaluator events
#   obstacles/goals : scripted sensor values
#   runtime_error : substring expected in the RuntimeError message
# ----------------------------------------------------------------------
M = lambda n: ("move", n)

TESTS = [
    dict(name="01 constants int/bool",
         src="""void main() { bool b; b = true; if (b) { move(5); } b = false;
                 if (!b) { move(1); } }""",
         has=["movl $5, %eax", "movl $1, %eax", "movl $0, %eax"],
         events=[M(5), M(1)]),

    dict(name="02 variable load/store",
         src="""void main() { int x; int y; x = 4; y = x; move(y); }""",
         has=["subl $8, %esp", "movl %eax, -4(%ebp)", "movl -4(%ebp), %eax",
              "movl %eax, -8(%ebp)"],
         events=[M(4)]),

    dict(name="03 arithmetic + - *",
         src="""void main() { move(2 + 3 * 4 - 1); }""",
         has=["addl %ebx, %eax", "subl %ebx, %eax", "imull %ebx, %eax"],
         events=[M(13)]),

    dict(name="04 signed division",
         src="""void main() { move(-7 / 2 + 10); move(9 / 3); }""",
         has=["cdq", "idivl %ebx", "negl %eax"],
         events=[M(7), M(3)]),

    dict(name="05 all comparisons",
         src="""void main() {
             if (1 < 2)  { move(1); }
             if (2 <= 2) { move(2); }
             if (3 > 2)  { move(3); }
             if (3 >= 3) { move(4); }
             if (1 == 1) { move(5); }
             if (1 != 2) { move(6); }
             if (2 < 1)  { move(99); }
             if (1 == 2) { move(99); }
         }""",
         has=["setl %al", "setle %al", "setg %al", "setge %al",
              "sete %al", "setne %al", "movzbl %al, %eax"],
         events=[M(1), M(2), M(3), M(4), M(5), M(6)]),

    dict(name="06 unary - and !",
         src="""void main() { move(-(-3)); if (!false) { move(1); }
                 if (!true) { move(99); } }""",
         has=["negl %eax", "sete %al"],
         events=[M(3), M(1)]),

    dict(name="07 short-circuit && and ||",
         src="""bool f() { move(1); return true; }
         void main() {
             if (false && f()) { move(9); }
             if (true || f())  { move(2); }
             if (true && f())  { move(3); }
             if (false || f()) { move(4); }
         }""",
         has=["je .L_and_final", "jne .L_or_final"],
         # f() must NOT run in the first two ifs
         events=[M(2), M(1), M(3), M(1), M(4)]),

    dict(name="08 if / if-else",
         src="""void main() {
             int x; x = 3;
             if (x > 5) { move(1); } else { move(2); }
             if (x < 5) { move(3); } else { move(4); }
             if (x == 3) { move(5); }
         }""",
         has=["je .L_else", "jmp .L_if_final"],
         events=[M(2), M(3), M(5)]),

    dict(name="09 while",
         src="""void main() { int i; i = 0;
                 while (i < 3) { move(1); i = i + 1; } }""",
         has=[".L_while_start", "je .L_while_final", "jmp .L_while_start"],
         events=[M(1), M(1), M(1)]),

    dict(name="10 nested while + if (independent labels)",
         src="""void main() {
             int i; int j; i = 0;
             while (i < 2) {
                 j = 0;
                 while (j < 2) {
                     if (j == 1) { move(2); } else { move(1); }
                     j = j + 1;
                 }
                 i = i + 1;
             }
         }""",
         events=[M(1), M(2), M(1), M(2)]),

    dict(name="11 move and turn",
         src="""void main() { move(2); turn(LEFT); turn(RIGHT); }""",
         has=["call neo_move", "movl $0, %eax\n    call neo_turn",
              "movl $1, %eax\n    call neo_turn"],
         events=[M(2), ("turn", "LEFT"), ("turn", "RIGHT")]),

    dict(name="12 obstacle() and goal()",
         src="""void main() {
             if (obstacle()) { turn(LEFT); } else { move(1); }
             if (goal()) { move(7); }
         }""",
         has=["call neo_obstacle", "call neo_goal"],
         obstacles=[True], goals=[True],
         events=[("turn", "LEFT"), M(7)]),

    dict(name="13 function with 1 parameter + return",
         src="""int inc(int x) { return x + 1; }
         void main() { move(inc(4)); }""",
         has=["movl 8(%ebp), %eax", "call inc", "addl $4, %esp",
              "leave", "ret"],
         events=[M(5)]),

    dict(name="14 function with 2 parameters (argument order)",
         src="""int sub(int a, int b) { return a - b; }
         void main() { move(sub(5, 2)); }""",
         has=["8(%ebp)", "12(%ebp)", "call sub", "addl $8, %esp"],
         order=[r"movl \$2, %eax\n\s+pushl %eax", r"movl \$5, %eax\n\s+pushl %eax",
                r"call sub"],
         events=[M(3)]),

    dict(name="15 void function called as a statement",
         src="""void go(int n) { move(n); turn(LEFT); }
         void main() { go(2); go(3); }""",
         has=["call go"],
         events=[M(2), ("turn", "LEFT"), M(3), ("turn", "LEFT")]),

    dict(name="16 recursion (factorial)",
         src="""int fact(int n) {
             if (n <= 1) { return 1; }
             return n * fact(n - 1);
         }
         void main() { move(fact(3)); }""",
         has=["call fact", "addl $4, %esp"],
         events=[M(6)]),

    dict(name="17 recursion (fibonacci, two calls)",
         src="""int fib(int n) {
             if (n < 2) { return n; }
             return fib(n - 1) + fib(n - 2);
         }
         void main() { move(fib(5)); }""",
         events=[M(5)]),

    dict(name="18 array assignment and access (constant index)",
         src="""void main() { int a[3]; a[0] = 4; a[2] = 6; move(a[0] + a[2]); }""",
         has=["subl $12, %esp", "-12(%ebp,%ecx,4)"],
         events=[M(10)]),

    dict(name="19 array indexed by a variable",
         src="""void main() { int a[2]; int i; i = 1; a[i] = 5; move(a[i]); }""",
         has=["subl $12, %esp", "-8(%ebp,%ecx,4)", "popl %ecx"],
         events=[M(5)]),

    dict(name="20 bool array",
         src="""void main() { bool f[2]; f[1] = true;
                 if (f[1]) { move(1); } if (f[0]) { move(99); } }""",
         events=[M(1)]),

    dict(name="21 array filled in a loop",
         src="""void main() {
             int a[3]; int i; int s;
             i = 0;
             while (i < 3) { a[i] = i + 1; i = i + 1; }
             s = 0; i = 0;
             while (i < 3) { s = s + a[i]; i = i + 1; }
             move(s);
         }""",
         events=[M(6)]),

    dict(name="22 block scopes / declarations in nested blocks",
         src="""void main() {
             int x; x = 1;
             if (true) { int y; y = 2; move(x + y); }
             else { int z; z = 9; move(z); }
             while (x < 3) { int w; w = x; move(w); x = x + 1; }
         }""",
         events=[M(3), M(1), M(2)]),

    dict(name="23 function call inside array index and arguments",
         src="""int two() { return 2; }
         int add(int a, int b) { return a + b; }
         void main() { int a[3]; a[two()] = add(two(), 3); move(a[two()]); }""",
         events=[M(5)]),

    dict(name="24 PDF final integration (no obstacles)",
         src="""int nextStep(int current) { return current + 1; }
         void main() {
             int steps[3]; int i;
             steps[0] = 1; steps[1] = 1; steps[2] = 1;
             i = 0;
             while (i < 3 && !goal()) {
                 if (!obstacle()) { move(steps[i]); } else { turn(RIGHT); }
                 i = nextStep(i);
             }
         }""",
         has=["subl $16, %esp", "call nextStep", "call neo_goal",
              "call neo_obstacle", "je .L_and_final"],
         events=[M(1), M(1), M(1)]),

    dict(name="25 PDF final integration (obstacle first, goal on 3rd check)",
         src="""int nextStep(int current) { return current + 1; }
         void main() {
             int steps[3]; int i;
             steps[0] = 1; steps[1] = 1; steps[2] = 1;
             i = 0;
             while (i < 3 && !goal()) {
                 if (!obstacle()) { move(steps[i]); } else { turn(RIGHT); }
                 i = nextStep(i);
             }
         }""",
         obstacles=[True, False], goals=[False, False, True],
         events=[("turn", "RIGHT"), M(1)]),
]

# Programs that must be rejected at compile time (front end, still part of P8)
COMPILE_ERRORS = [
    ("E1 int = bool",           "void main() { int x; x = true; }", SemanticError),
    ("E2 missing main",         "int f() { return 1; }", SemanticError),
    ("E3 void used in expr",    "void g() { move(1); } void main() { move(g()); }", SemanticError),
    ("E4 wrong arg count",      "int f(int a) { return a; } void main() { move(f(1, 2)); }", SemanticError),
    ("E5 non-bool condition",   "void main() { if (1) { move(1); } }", SemanticError),
    ("E6 undeclared variable",  "void main() { x = 1; }", SemanticError),
    ("E7 duplicate variable",   "void main() { int x; int x; }", SemanticError),
    ("E8 index a scalar",       "void main() { int x; x[0] = 1; }", SemanticError),
    ("E9 syntax error",         "void main() { move(1) }", SyntaxError),
    ("E10 lexical error",       "void main() { move(1) @ }", ValueError),
]

# Programs that compile but must fail at run time (evaluator responsibility)
RUNTIME_ERRORS = [
    ("R1 division by zero", "void main() { move(1 / 0); }", "division by zero"),
    ("R2 array out of bounds", "void main() { int a[2]; a[2] = 1; }", "out of bounds"),
]


# ----------------------------------------------------------------------
# Runner
# ----------------------------------------------------------------------
def main():
    args = [a for a in sys.argv[1:] if not a.startswith("-")]
    verbose = "-v" in sys.argv
    flt = args[0].lower() if args else None

    passed = failed = 0

    def report(name, errors):
        nonlocal passed, failed
        if errors:
            failed += 1
            print(f"FAIL  {name}")
            for e in errors:
                print(f"        - {e}")
        else:
            passed += 1
            print(f"ok    {name}")

    for t in TESTS:
        if flt and flt not in t["name"].lower():
            continue
        errors = []
        try:
            ast, asm = compile_neo(t["src"])
            if verbose:
                print(f"\n----- {t['name']} -----\n{asm}")
            for s in t.get("has", []):
                if s not in asm:
                    errors.append(f"assembly is missing: {s!r}")
            for s in t.get("hasnt", []):
                if s in asm:
                    errors.append(f"assembly must not contain: {s!r}")
            if "order" in t:
                ok, bad = in_order(asm, t["order"])
                if not ok:
                    errors.append(f"expected pattern (in order) not found: {bad!r}")
            errors += check_asm_sanity(asm)
            if "events" in t:
                got = run_neo(ast, t.get("obstacles"), t.get("goals"))
                if got != t["events"]:
                    errors.append(f"events: expected {t['events']}, got {got}")
        except Exception as exc:
            errors.append(f"{type(exc).__name__}: {exc}")
        report(t["name"], errors)

    for name, src, exc_type in COMPILE_ERRORS:
        if flt and flt not in name.lower():
            continue
        try:
            compile_neo(src)
            report(name, [f"expected {exc_type.__name__}, but it compiled"])
        except exc_type:
            report(name, [])
        except Exception as exc:
            report(name, [f"expected {exc_type.__name__}, got {type(exc).__name__}: {exc}"])

    for name, src, msg in RUNTIME_ERRORS:
        if flt and flt not in name.lower():
            continue
        try:
            ast, asm = compile_neo(src)
            run_neo(ast)
            report(name, ["expected a RuntimeError, but the program finished"])
        except RuntimeError as exc:
            report(name, [] if msg in str(exc) else [f"unexpected message: {exc}"])
        except Exception as exc:
            report(name, [f"{type(exc).__name__}: {exc}"])

    print(f"\n{passed} passed, {failed} failed")
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()