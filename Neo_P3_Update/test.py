from compiler.lexer import NeoLexer
from compiler.parser import NeoParser

tests = [
    "int x; int x;",
    "y = 3;",
    "int x; x = other + 1;",
    "x = 2; int x;",
    "int a; int b; a = 1; b = a * 2 + a; move(b);",
    "int x = 5;",
]

for src in tests:
    print("SRC:", src)
    try:
        p = NeoParser()
        print("  ", p.parse(NeoLexer().tokenize(src)))
        print("  ", p.symbol_table.symbols)
    except Exception as e:
        print("  ", type(e).__name__, e)

p = NeoParser()
p.parse(NeoLexer().tokenize("int x;"))
p.parse(NeoLexer().tokenize("int x;"))
print("reuse OK")