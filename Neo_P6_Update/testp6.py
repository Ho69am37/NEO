from compiler.lexer import NeoLexer
from compiler.parser import NeoParser
from compiler.symbol_table import SemanticError
from compiler.ast_nodes import Program, FunctionDefinition, FunctionCall

results = []


def parse(src):
    return NeoParser().parse(NeoLexer().tokenize(src))


def check(label, ok, detail=""):
    results.append(ok)
    print(f"[{'OK' if ok else 'FAIL'}] {label}" + (f"  {detail}" if detail else ""))


def valid(label, src):
    try:
        prog = parse(src)
        check(label, isinstance(prog, Program))
    except Exception as ex:
        check(label, False, f"{type(ex).__name__}: {ex}")


def error(label, src, exc_type):
    try:
        parse(src)
        check(label, False, "was accepted")
    except exc_type as ex:
        check(label, True, f"-> {ex}")
    except Exception as ex:
        check(label, False, f"wrong exception {type(ex).__name__}: {ex}")


print("=== Valid programs ===")
valid("void function without parameters",
      "void hello() { move(1); } void main() { hello(); }")

valid("function with parameters",
      "void advance(int n, bool b) { move(n); } void main() { advance(2, true); }")

valid("int function returning a value",
      "int dbl(int x) { return x * 2; } void main() { int s; s = dbl(1); move(s); }")

valid("bool function returning a value",
      "bool pos(int x) { return x > 0; } void main() { if (pos(3)) { move(1); } }")

valid("call inside an expression",
      "int dbl(int x) { return x * 2; } void main() { move(dbl(1) + dbl(2) * 3); }")

valid("recursive function",
      """int fact(int n) {
             if (n == 0) { return 1; }
             return n * fact(n - 1);
         }
         void main() { move(fact(3)); }""")

valid("shadowing in a nested block",
      "void main() { int x; x = 1; if (true) { int x; x = 2; move(x); } move(x); }")

valid("non-void function that may reach the end (must pass)",
      "int f(int x) { if (x > 0) { return 1; } } void main() { move(f(1)); }")

print("\n=== Semantic errors ===")
error("variable used after leaving its scope",
      "void main() { if (true) { int y; y = 1; } move(y); }", SemanticError)
error("wrong argument count",
      "int f(int a) { return a; } void main() { move(f(1, 2)); }", SemanticError)
error("too few arguments",
      "int f(int a) { return a; } void main() { move(f()); }", SemanticError)
error("wrong argument type",
      "int f(int a) { return a; } void main() { move(f(true)); }", SemanticError)
error("wrong return type",
      "bool f() { return 1; } void main() { move(1); }", SemanticError)
error("return in a void function",
      "void f() { return 1; } void main() { move(1); }", SemanticError)
error("void call used in an expression",
      "void f() { move(1); } void main() { move(f()); }", SemanticError)
error("non-void call as a statement",
      "int f() { return 1; } void main() { f(); }", SemanticError)
error("undefined function",
      "void main() { g(); }", SemanticError)
error("undefined variable",
      "void main() { x = 1; }", SemanticError)
error("duplicate declaration in same scope",
      "void main() { int x; int x; }", SemanticError)
error("duplicate parameter",
      "void f(int a, int a) { move(a); } void main() { move(1); }", SemanticError)
error("main with parameters",
      "void main(int a) { move(a); }", SemanticError)
error("main not void",
      "int main() { return 1; }", SemanticError)
error("missing main",
      "void f() { move(1); }", SemanticError)
error("function used before its definition",
      "void main() { g(); } void g() { move(1); }", SemanticError)
error("non-bool condition",
      "void main() { int x; x = 1; while (x) { move(1); } }", SemanticError)

print("\n=== Syntax errors ===")
error("statement at global level", "move(1);", SyntaxError)
error("empty block", "void main() { if (true) { } }", SyntaxError)
error("nested function", "void main() { void f() { move(1); } }", SyntaxError)

print("\n=== AST shape ===")
try:
    prog = parse("int f(int a) { return a; } void main() { move(f(1)); }")
    f, m = prog.functions
    ok = (isinstance(f, FunctionDefinition) and f.name == "f"
          and f.return_type == "int" and len(f.parameters) == 1
          and m.name == "main" and m.body.statements[0].expression.type == "int"
          and isinstance(m.body.statements[0].expression, FunctionCall))
    check("FunctionDefinition / FunctionCall built correctly", ok)
except Exception as ex:
    check("FunctionDefinition / FunctionCall built correctly", False, str(ex))

print(f"\n{sum(results)} passed, {len(results) - sum(results)} failed")